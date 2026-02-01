from rest_framework import serializers
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Equipment model.
    Converts equipment data to/from JSON.
    """
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
        ]
        read_only_fields = ['id', 'is_pressure_outlier', 'is_temperature_outlier']


class DatasetSerializer(serializers.ModelSerializer):
    """
    Serializer for Dataset model with nested equipment data.
    """
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
        """Return the count of equipment in this dataset."""
        return obj.equipment.count()


class DatasetListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for dataset list view (without equipment details).
    """
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
        ]

    def get_equipment_count(self, obj):
        return obj.equipment.count()


class AnalyticsSerializer(serializers.Serializer):
    """
    Serializer for analytics data (not tied to a model).
    """
    total_equipment = serializers.IntegerField()
    avg_flowrate = serializers.FloatField()
    avg_pressure = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    equipment_type_distribution = serializers.DictField()
    outliers_count = serializers.IntegerField()
    outlier_equipment = serializers.ListField()