from django.contrib import admin
from .models import Dataset, Equipment


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['filename', 'uploaded_at', 'total_equipment', 'avg_flowrate', 'avg_pressure', 'avg_temperature']
    list_filter = ['uploaded_at']
    search_fields = ['filename']
    readonly_fields = ['id', 'uploaded_at']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'is_pressure_outlier', 'is_temperature_outlier']
    list_filter = ['equipment_type', 'is_pressure_outlier', 'is_temperature_outlier']
    search_fields = ['equipment_name']
    readonly_fields = ['id']