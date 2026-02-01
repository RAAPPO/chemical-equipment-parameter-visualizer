"""
Django Admin customization - Professional display.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Dataset, Equipment


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """Admin interface for Dataset model."""
    
    list_display = [
        'filename',
        'uploaded_at',
        'total_equipment',
        'avg_flowrate_display',
        'avg_pressure_display',
        'avg_temperature_display',
    ]
    list_filter = ['uploaded_at']
    search_fields = ['filename']
    readonly_fields = ['id', 'uploaded_at', 'total_equipment']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Dataset Information', {
            'fields': ('id', 'filename', 'uploaded_at', 'total_equipment')
        }),
        ('Statistics', {
            'fields': ('avg_flowrate', 'avg_pressure', 'avg_temperature'),
            'description': 'Average parameter values across all equipment'
        }),
    )
    
    def avg_flowrate_display(self, obj):
        """Format average flowrate."""
        return f"{obj.avg_flowrate:.2f}" if obj.avg_flowrate else "N/A"
    avg_flowrate_display.short_description = "Avg Flowrate"
    avg_flowrate_display.admin_order_field = 'avg_flowrate'
    
    def avg_pressure_display(self, obj):
        """Format average pressure."""
        return f"{obj.avg_pressure:.2f}" if obj.avg_pressure else "N/A"
    avg_pressure_display.short_description = "Avg Pressure"
    avg_pressure_display.admin_order_field = 'avg_pressure'
    
    def avg_temperature_display(self, obj):
        """Format average temperature."""
        return f"{obj.avg_temperature:.2f}" if obj.avg_temperature else "N/A"
    avg_temperature_display.short_description = "Avg Temperature"
    avg_temperature_display.admin_order_field = 'avg_temperature'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Admin interface for Equipment model."""
    
    list_display = [
        'equipment_name',
        'equipment_type',
        'dataset_link',
        'flowrate',
        'pressure',
        'temperature',
        'outlier_status',
    ]
    list_filter = [
        'equipment_type',
        'is_pressure_outlier',
        'is_temperature_outlier',
        'dataset__uploaded_at',
    ]
    search_fields = ['equipment_name', 'dataset__filename']
    readonly_fields = ['id', 'is_pressure_outlier', 'is_temperature_outlier']
    
    fieldsets = (
        ('Equipment Information', {
            'fields': ('id', 'dataset', 'equipment_name', 'equipment_type')
        }),
        ('Parameters', {
            'fields': ('flowrate', 'pressure', 'temperature')
        }),
        ('Outlier Detection', {
            'fields': ('is_pressure_outlier', 'is_temperature_outlier'),
            'description': 'Automatically detected using Z-score method (threshold: 2.0)'
        }),
    )
    
    def dataset_link(self, obj):
        """Link to parent dataset."""
        return format_html(
            '<a href="/admin/api/dataset/{}/change/">{}</a>',
            obj.dataset.id,
            obj.dataset.filename
        )
    dataset_link.short_description = "Dataset"
    
    def outlier_status(self, obj):
        """Visual indicator for outliers."""
        if obj.is_outlier:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ OUTLIER</span>'
            )
        return format_html(
            '<span style="color: green;">✓ Normal</span>'
        )
    outlier_status.short_description = "Status"
    outlier_status.admin_order_field = 'is_pressure_outlier'