"""
Business logic layer - separates data processing from views.
Industry best practice: Fat services, thin views.
"""
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
        
        Args:
            file: Uploaded CSV file object
            
        Returns:
            pd.DataFrame: Validated and cleaned data
            
        Raises:
            CSVValidationError: If validation fails
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
            invalid_types = df[~df['Type'].isin(valid_types)]['Type'].unique()
            if len(invalid_types) > 0:
                # Map to 'Other' instead of failing
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
        """
        Detect outliers using Z-score method.
        
        Args:
            values: Array of numeric values
            threshold: Z-score threshold (default: 2.0)
            
        Returns:
            Boolean array indicating outliers
        """
        if len(values) < 3:
            return np.zeros(len(values), dtype=bool)

        mean = np.mean(values)
        std = np.std(values, ddof=1)  # Sample std deviation (n-1)

        if std == 0 or np.isnan(std):
            return np.zeros(len(values), dtype=bool)
        
        z_scores = np.abs((values - mean) / std)
        return z_scores > threshold
    
    @staticmethod
    @transaction.atomic
    def create_dataset_from_csv(file: BinaryIO, filename: str) -> Dataset:
        """
        Process CSV and create Dataset with Equipment records.
        Uses database transaction for atomicity.
        
        Args:
            file: Uploaded CSV file
            filename: Original filename
            
        Returns:
            Dataset: Created dataset instance
        """
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
        
        # Bulk create equipment records (more efficient than individual creates)
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

            # Convert to DataFrame for advanced Pandas analytics
            df = pd.DataFrame(list(equipment_qs.values(
                'equipment_type', 'flowrate', 'pressure', 'temperature'
            )))

            # Calculate Pearson Correlation between Pressure and Temp
            correlation = df['pressure'].corr(df['temperature']) if len(df) > 1 else 0

            # Peer Benchmarking: Avg parameters grouped by Type
            peer_stats = df.groupby('equipment_type').agg({
                'flowrate': 'mean',
                'pressure': 'mean',
                'temperature': 'mean'
            }).round(2).to_dict('index')

            # Get original analytics from model for outliers/counts
            base_analytics = dataset.get_analytics()

            # Merge with advanced insights
            base_analytics.update({
                'pt_correlation': round(correlation, 3),
                'peer_benchmarks': peer_stats,
                # Prepare data for Scatter Plot (P vs T)
                'scatter_data': [
                    {'x': eq.pressure, 'y': eq.temperature, 'name': eq.equipment_name}
                    for eq in equipment_qs
                ]
            })
            return base_analytics
        except Dataset.DoesNotExist:
            raise ValueError(f"Dataset {dataset_id} not found")