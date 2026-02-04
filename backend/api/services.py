
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
        """
        Validate CSV structure and return cleaned DataFrame.
        """
        try:
            content = file.read().decode('utf-8')
            df = pd.read_csv(StringIO(content))
            
            # Check required columns
            missing_cols = [col for col in DatasetService.REQUIRED_COLUMNS if col not in df.columns]
            if missing_cols:
                raise CSVValidationError(f"Missing required columns: {', '.join(missing_cols)}")
            
            # Validate data types
            numeric_columns = ['Flowrate', 'Pressure', 'Temperature']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove invalid rows
            df = df.dropna(subset=numeric_columns)
            
            if df.empty:
                raise CSVValidationError("No valid data rows found after cleaning")
            
            # Validate equipment types
            valid_types = [choice[0] for choice in Equipment.EquipmentType.choices]
            # Map invalid types to 'Other'
            df.loc[~df['Type'].isin(valid_types), 'Type'] = 'Other'
            
            return df
        
        except pd.errors.EmptyDataError:
            raise CSVValidationError("CSV file is empty")
        except UnicodeDecodeError:
            raise CSVValidationError("Invalid file encoding (expected UTF-8)")
        except Exception as e:
            raise CSVValidationError(f"CSV validation failed: {str(e)}")
    
    @staticmethod
    def detect_outliers(values: np.ndarray, threshold: float = 2.0) -> np.ndarray:
        """Detect outliers using Z-score method."""
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
        """Process CSV and create Dataset with Equipment records."""
        # Validate and parse CSV
        df = DatasetService.validate_csv(file)
        
        # Calculate statistics
        stats = {
            'total_equipment': len(df),
            'avg_flowrate': round(df['Flowrate'].mean(), 2),
            'avg_pressure': round(df['Pressure'].mean(), 2),
            'avg_temperature': round(df['Temperature'].mean(), 2),
        }
        
        # Create dataset
        dataset = Dataset.objects.create(filename=filename, **stats)
        
        # Detect outliers
        pressure_outliers = DatasetService.detect_outliers(df['Pressure'].values)
        temperature_outliers = DatasetService.detect_outliers(df['Temperature'].values)
        
        # Bulk create equipment records
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
        """
        Generate advanced analytics for the Dynamic Dashboard.
        Includes Correlations, Box Plot stats, and Benchmarks.
        """
        try:
            dataset = Dataset.objects.prefetch_related('equipment').get(id=dataset_id)
            equipment_qs = dataset.equipment.all()

            # Convert to DataFrame for advanced Pandas analytics
            df = pd.DataFrame(list(equipment_qs.values(
                'equipment_type', 'flowrate', 'pressure', 'temperature'
            )))

            if df.empty:
                raise ValueError("Dataset has no equipment data")

            # 1. Basic Correlation (Scalar)
            correlation = df['pressure'].corr(df['temperature']) if len(df) > 1 else 0

            # 2. Peer Benchmarking: Avg parameters grouped by Type
            peer_stats = df.groupby('equipment_type').agg({
                'flowrate': 'mean',
                'pressure': 'mean',
                'temperature': 'mean'
            }).round(2).to_dict('index')

            # 3. Distribution Stats (For Box Plots - Quartiles)
            # Calculating for Flowrate
            flow_desc = df['flowrate'].describe(percentiles=[.25, .5, .75])
            distribution_stats = {
                'min': round(flow_desc['min'], 2),
                'q1': round(flow_desc['25%'], 2),
                'median': round(flow_desc['50%'], 2),
                'q3': round(flow_desc['75%'], 2),
                'max': round(flow_desc['max'], 2)
            }

            # 4. Full Correlation Matrix (For Heatmap)
            # Returns list of dicts: [{'variable': 'flowrate', 'flowrate': 1.0, 'pressure': 0.8...}, ...]
            corr_df = df[['flowrate', 'pressure', 'temperature']].corr().round(2)
            correlation_matrix = corr_df.reset_index().rename(columns={'index': 'variable'}).to_dict('records')

            # Get original analytics from model for outliers/counts
            base_analytics = dataset.get_analytics()

            # Merge all insights
            base_analytics.update({
                'pt_correlation': round(correlation, 3),
                'peer_benchmarks': peer_stats,
                'distribution_stats': distribution_stats,
                'correlation_matrix': correlation_matrix,
                # Enhanced Scatter Data (Added 'type' for color and 'r' for bubble size)
                'scatter_data': [
                    {
                        'x': eq.pressure, 
                        'y': eq.temperature, 
                        'r': max(2, eq.flowrate / 15), # Scaled radius for Bubble Chart
                        'name': eq.equipment_name,
                        'type': eq.equipment_type
                    }
                    for eq in equipment_qs
                ]
            })
            return base_analytics
        except Dataset.DoesNotExist:
            raise ValueError(f"Dataset {dataset_id} not found")