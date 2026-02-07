"""
Default Django Admin Configuration
"""
from django.contrib import admin
from .models import Dataset, Equipment


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['filename', 'uploaded_at', 'total_equipment']
    list_filter = ['uploaded_at']
    search_fields = ['filename']
    readonly_fields = ['id', 'uploaded_at', 'total_equipment']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'dataset', 'flowrate', 'pressure', 'temperature']
    list_filter = ['equipment_type', 'is_pressure_outlier', 'is_temperature_outlier']
    search_fields = ['equipment_name', 'equipment_type']
    readonly_fields = ['id', 'is_pressure_outlier', 'is_temperature_outlier']