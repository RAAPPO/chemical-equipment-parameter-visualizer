
import pandas as pd
import numpy as np
from typing import Dict, Any, BinaryIO
from io import StringIO
from django.db import transaction
from .models import Dataset, Equipment


class CSVValidationError(Exception):
    """Custom exception for CSV validation errors."""
    pass


class DatasetService:
    """Service class for dataset-related business logic."""
    
    REQUIRED_COLUMNS = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
    CHUNK_SIZE = 1000  # Process large CSVs in chunks
    
    @staticmethod
    def validate_csv(file: BinaryIO) -> pd.DataFrame:
        try:
            content = file.read().decode('utf-8')
            df = pd.read_csv(StringIO(content))
            
            missing_cols = [col for col in DatasetService.REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                raise CSVValidationError(f"Missing required columns: {', '.join(missing_cols)}")
            
            numeric_columns = ['Flowrate', 'Pressure', 'Temperature']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=numeric_columns)
            
            if df.empty:
                raise CSVValidationError("No valid data rows found after cleaning")
            
            # Normalize Types (Capitalize first letter to ensure consistency for Filtering)
            df['Type'] = df['Type'].astype(str).str.strip().str.capitalize()
            
            return df
        
        except pd.errors.EmptyDataError:
            raise CSVValidationError("CSV file is empty")
        except UnicodeDecodeError:
            raise CSVValidationError("Invalid file encoding (expected UTF-8)")
        except Exception as e:
            raise CSVValidationError(f"CSV validation failed: {str(e)}")
    
    @staticmethod
    def detect_outliers(values: np.ndarray, threshold: float = 2.0) -> np.ndarray:
        if len(values) < 3:
            return np.zeros(len(values), dtype=bool)

        mean = np.mean(values)
        std = np.std(values, ddof=1)

        if std == 0 or np.isnan(std):
            return np.zeros(len(values), dtype=bool)
        
        z_scores = np.abs((values - mean) / std)
        return z_scores > threshold
    
    @staticmethod
    @transaction.atomic
    def create_dataset_from_csv(file: BinaryIO, filename: str) -> Dataset:
        df = DatasetService.validate_csv(file)
        
        stats = {
            'total_equipment': len(df),
            'avg_flowrate': round(df['Flowrate'].mean(), 2),
            'avg_pressure': round(df['Pressure'].mean(), 2),
            'avg_temperature': round(df['Temperature'].mean(), 2),
        }
        
        dataset = Dataset.objects.create(filename=filename, **stats)
        
        pressure_outliers = DatasetService.detect_outliers(df['Pressure'].values)
        temperature_outliers = DatasetService.detect_outliers(df['Temperature'].values)
        
        equipment_objects = [
            Equipment(
                dataset=dataset,
                equipment_name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=row['Flowrate'],
                pressure=row['Pressure'],
                temperature=row['Temperature'],
                is_pressure_outlier=bool(pressure_outliers[idx]),
                is_temperature_outlier=bool(temperature_outliers[idx]),
            )
            for idx, row in df.iterrows()
        ]
        
        Equipment.objects.bulk_create(equipment_objects, batch_size=DatasetService.CHUNK_SIZE)
        
        return dataset
    
    @staticmethod
    def get_analytics(dataset_id: str) -> Dict[str, Any]:
        try:
            dataset = Dataset.objects.prefetch_related('equipment').get(id=dataset_id)
            equipment_qs = dataset.equipment.all()

            # Create DataFrame for advanced analytics
            df = pd.DataFrame(list(equipment_qs.values(
                'equipment_type', 'flowrate', 'pressure', 'temperature', 'equipment_name'
            )))

            if df.empty:
                 raise ValueError("Dataset has no equipment data")

            # 1. Correlations
            correlation = df['pressure'].corr(df['temperature']) if len(df) > 1 else 0
            
            # Full Correlation Matrix for Heatmap
            corr_df = df[['flowrate', 'pressure', 'temperature']].corr().round(2).fillna(0)
            correlation_matrix = corr_df.reset_index().rename(columns={'index': 'variable'}).to_dict('records')

            # 2. Peer Benchmarking & Ranges (Min/Max for Floating Bars)
            peer_stats = df.groupby('equipment_type').agg({
                'flowrate': ['mean', 'min', 'max'],
                'pressure': 'mean',
                'temperature': 'mean'
            }).round(2)
            
            # Flatten the MultiIndex columns
            peer_stats.columns = ['_'.join(col).strip() for col in peer_stats.columns.values]
            peer_stats_dict = peer_stats.to_dict('index')

            # 3. Distribution Stats (Quartiles for Box Plot visualizations)
            desc = df[['flowrate', 'pressure', 'temperature']].describe(percentiles=[.25, .5, .75]).round(2)
            distribution_stats = desc.to_dict()

            base_analytics = dataset.get_analytics()

            base_analytics.update({
                'pt_correlation': round(correlation, 3),
                'peer_benchmarks': peer_stats_dict,
                'distribution_stats': distribution_stats,
                'correlation_matrix': correlation_matrix,
                # Enhanced Scatter Data: Include Type (for filtering) and Flowrate (for bubbles)
                'scatter_data': [
                    {
                        'x': row['pressure'], 
                        'y': row['temperature'], 
                        'r': row['flowrate'], 
                        'name': row['equipment_name'],
                        'type': row['equipment_type'] 
                    }
                    for _, row in df.iterrows()
                ]
            })
            return base_analytics
        except Dataset.DoesNotExist:
            raise ValueError(f"Dataset {dataset_id} not found")