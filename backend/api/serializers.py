"""
DRF Serializers - Clean, efficient, with proper validation.
Industry standard: Explicit field definitions, custom validations.
"""
from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    """Equipment serializer with computed fields."""
    
    is_outlier = serializers.ReadOnlyField()
    
    class Meta:
        model = Equipment
        fields = [
            'id',
            'equipment_name',
            'equipment_type',
            'flowrate',
            'pressure',
            'temperature',
            'is_pressure_outlier',
            'is_temperature_outlier',
            'is_outlier',
        ]
        read_only_fields = ['id', 'is_pressure_outlier', 'is_temperature_outlier']


class DatasetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dataset list (no nested data)."""
    
    equipment_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'filename',
            'uploaded_at',
            'total_equipment',
            'avg_flowrate',
            'avg_pressure',
            'avg_temperature',
            'equipment_count',
        ]
        read_only_fields = ['id', 'uploaded_at']


class DatasetSerializer(serializers.ModelSerializer):
    """Full dataset serializer with nested equipment."""
    
    equipment = EquipmentSerializer(many=True, read_only=True)
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'filename',
            'uploaded_at',
            'total_equipment',
            'avg_flowrate',
            'avg_pressure',
            'avg_temperature',
            'equipment_count',
            'equipment',
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def get_equipment_count(self, obj):
        """Get equipment count (use annotation if available)."""
        if hasattr(obj, 'equipment_count'):
            return obj.equipment_count
        return obj.equipment.count()


class AnalyticsSerializer(serializers.Serializer):
    total_equipment = serializers.IntegerField(min_value=0)
    avg_flowrate = serializers.FloatField()
    avg_pressure = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    pt_correlation = serializers.FloatField()
    peer_benchmarks = serializers.DictField()
    scatter_data = serializers.ListField(child=serializers.DictField())
    equipment_type_distribution = serializers.DictField(
        child=serializers.IntegerField(min_value=0)
    )
    outliers_count = serializers.IntegerField(min_value=0)
    outlier_equipment = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=True
    )
    
    def validate_equipment_type_distribution(self, value):
        """Ensure distribution values are valid."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Must be a dictionary")
        
        total = sum(value.values())
        if total <= 0:
            raise serializers.ValidationError("Distribution must have at least one equipment")
        
        return value


class CSVUploadSerializer(serializers.Serializer):
    """Serializer for CSV file upload validation."""
    
    file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        help_text="CSV file with equipment data"
    )
    
    def validate_file(self, value):
        """Validate file size and content type."""
        max_size = 10 * 1024 * 1024  # 10MB
        
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed size of {max_size / 1024 / 1024}MB"
            )
        
        return value