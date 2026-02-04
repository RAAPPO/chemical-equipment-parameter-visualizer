
from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    is_outlier = serializers.ReadOnlyField()
    class Meta:
        model = Equipment
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'is_pressure_outlier', 'is_temperature_outlier', 'is_outlier']
        read_only_fields = ['id', 'is_pressure_outlier', 'is_temperature_outlier']

class DatasetListSerializer(serializers.ModelSerializer):
    equipment_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'total_equipment', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'equipment_count']
        read_only_fields = ['id', 'uploaded_at']

class DatasetSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(many=True, read_only=True)
    equipment_count = serializers.SerializerMethodField()
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'total_equipment', 'avg_flowrate', 'avg_pressure', 'avg_temperature', 'equipment_count', 'equipment']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_equipment_count(self, obj):
        if hasattr(obj, 'equipment_count'): return obj.equipment_count
        return obj.equipment.count()

class AnalyticsSerializer(serializers.Serializer):
    """Supports World-Class Dashboard Views"""
    total_equipment = serializers.IntegerField()
    avg_flowrate = serializers.FloatField()
    avg_pressure = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    
    # Advanced Stats
    pt_correlation = serializers.FloatField()
    peer_benchmarks = serializers.DictField()
    distribution_stats = serializers.DictField() # New
    correlation_matrix = serializers.ListField(child=serializers.DictField()) # New
    
    # Visualization Data
    scatter_data = serializers.ListField(child=serializers.DictField())
    equipment_type_distribution = serializers.DictField()
    outliers_count = serializers.IntegerField()
    outlier_equipment = serializers.ListField(child=serializers.DictField())

class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])])
    def validate_file(self, value):
        if value.size > 10 * 1024 * 1024: raise serializers.ValidationError("File too large (Max 10MB)")
        return value