import pandas as pd
import numpy as np
from io import StringIO
from .models import Dataset, Equipment


def validate_csv_structure(file):
    """
    Validate CSV file structure and return DataFrame.
    
    Args:
        file: Uploaded CSV file
        
    Returns:
        pd.DataFrame: Validated DataFrame
        
    Raises:
        ValueError: If CSV structure is invalid
    """
    try:
        # Read CSV
        content = file.read().decode('utf-8')
        df = pd.read_csv(StringIO(content))
        
        # Required columns
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Validate data types
        numeric_columns = ['Flowrate', 'Pressure', 'Temperature']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with missing critical data
        df = df.dropna(subset=numeric_columns)
        
        if df.empty:
            raise ValueError("CSV contains no valid data after cleaning")
        
        return df
    
    except Exception as e:
        raise ValueError(f"CSV validation failed: {str(e)}")


def detect_outliers(values):
    """
    Detect outliers using Z-score method.
    
    Args:
        values: Array of numeric values
        
    Returns:
        np.array: Boolean array indicating outliers (True = outlier)
    """
    if len(values) < 3:  # Need at least 3 values for meaningful statistics
        return np.zeros(len(values), dtype=bool)
    
    mean = np.mean(values)
    std = np.std(values)
    
    if std == 0:  # All values are identical
        return np.zeros(len(values), dtype=bool)
    
    z_scores = np.abs((values - mean) / std)
    return z_scores > 2  # Outliers have |Z-score| > 2


def process_csv_and_create_dataset(file, filename):
    """
    Process CSV file and create Dataset + Equipment records.
    
    Args:
        file: Uploaded CSV file
        filename: Name of the file
        
    Returns:
        Dataset: Created dataset instance
    """
    # Validate and parse CSV
    df = validate_csv_structure(file)
    
    # Calculate statistics
    total_equipment = len(df)
    avg_flowrate = df['Flowrate'].mean()
    avg_pressure = df['Pressure'].mean()
    avg_temperature = df['Temperature'].mean()
    
    # Create Dataset record
    dataset = Dataset.objects.create(
        filename=filename,
        total_equipment=total_equipment,
        avg_flowrate=round(avg_flowrate, 2),
        avg_pressure=round(avg_pressure, 2),
        avg_temperature=round(avg_temperature, 2),
    )
    
    # Detect outliers
    pressure_outliers = detect_outliers(df['Pressure'].values)
    temperature_outliers = detect_outliers(df['Temperature'].values)
    
    # Create Equipment records
    equipment_list = []
    for idx, row in df.iterrows():
        equipment = Equipment(
            dataset=dataset,
            equipment_name=row['Equipment Name'],
            equipment_type=row['Type'],
            flowrate=row['Flowrate'],
            pressure=row['Pressure'],
            temperature=row['Temperature'],
            is_pressure_outlier=bool(pressure_outliers[idx]),
            is_temperature_outlier=bool(temperature_outliers[idx]),
        )
        equipment_list.append(equipment)
    
    # Bulk create for efficiency
    Equipment.objects.bulk_create(equipment_list)
    
    return dataset


def get_analytics_for_dataset(dataset_id):
    """
    Calculate analytics for a specific dataset.
    
    Args:
        dataset_id: UUID of the dataset
        
    Returns:
        dict: Analytics data
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        equipment = dataset.equipment.all()
        
        # Equipment type distribution
        type_distribution = {}
        for eq in equipment:
            type_distribution[eq.equipment_type] = type_distribution.get(eq.equipment_type, 0) + 1
        
        # Outliers
        outliers = equipment.filter(is_pressure_outlier=True) | equipment.filter(is_temperature_outlier=True)
        outlier_list = [
            {
                'name': eq.equipment_name,
                'type': eq.equipment_type,
                'pressure_outlier': eq.is_pressure_outlier,
                'temperature_outlier': eq.is_temperature_outlier,
            }
            for eq in outliers.distinct()
        ]
        
        return {
            'total_equipment': dataset.total_equipment,
            'avg_flowrate': dataset.avg_flowrate,
            'avg_pressure': dataset.avg_pressure,
            'avg_temperature': dataset.avg_temperature,
            'equipment_type_distribution': type_distribution,
            'outliers_count': len(outlier_list),
            'outlier_equipment': outlier_list,
        }
    
    except Dataset.DoesNotExist:
        raise ValueError(f"Dataset with id {dataset_id} not found")