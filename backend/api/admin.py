"""
Custom Django Admin Configuration
Professional admin interface with enhanced features
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe  # Added this import
from django.urls import reverse
from django.db.models import Count, Q
from .models import Dataset, Equipment
import logging

logger = logging.getLogger(__name__)


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """Enhanced Dataset admin with custom actions and display"""
    
    list_display = [
        'filename_display',
        'uploaded_at',
        'equipment_count_display',
        'avg_flowrate_display',
        'avg_pressure_display',
        'avg_temperature_display',
        'outlier_count_display',
        'actions_display'
    ]
    
    list_filter = [
        'uploaded_at',
        'total_equipment',  # FIXED: Removed EmptyFieldListFilter
    ]
    
    search_fields = ['filename', 'id']
    
    readonly_fields = [
        'id',
        'uploaded_at',
        'total_equipment',
        'avg_flowrate',
        'avg_pressure',
        'avg_temperature',
        'equipment_preview'
    ]
    
    fieldsets = (
        ('Dataset Information', {
            'fields': ('id', 'filename', 'uploaded_at')
        }),
        ('Statistics', {
            'fields': (
                'total_equipment',
                'avg_flowrate',
                'avg_pressure',
                'avg_temperature'
            ),
            'classes': ('collapse',)
        }),
        ('Equipment Preview', {
            'fields': ('equipment_preview',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['export_selected_csv', 'delete_with_equipment', 'recalculate_stats']
    
    def get_queryset(self, request):
        """Optimize queries with annotations"""
        qs = super().get_queryset(request)
        qs = qs.annotate(
            _equipment_count=Count('equipment'),
            _outlier_count=Count('equipment', filter=Q(
                equipment__is_pressure_outlier=True
            ) | Q(
                equipment__is_temperature_outlier=True
            ))
        )
        return qs
    
    def filename_display(self, obj):
        """Display filename with icon"""
        return format_html(
            '<span style="font-weight: bold;">📄 {}</span>',
            obj.filename
        )
    filename_display.short_description = 'Dataset File'
    filename_display.admin_order_field = 'filename'
    
    def equipment_count_display(self, obj):
        """Display equipment count with badge"""
        count = getattr(obj, '_equipment_count', obj.total_equipment)
        color = '#10B981' if count > 0 else '#EF4444'
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-weight: bold;">{}</span>',
            color, count
        )
    equipment_count_display.short_description = 'Equipment'
    equipment_count_display.admin_order_field = 'total_equipment'
    
    def avg_flowrate_display(self, obj):
        """Display average flowrate"""
        if obj.avg_flowrate is not None:
            # FIXED: Format number first, then pass to format_html
            formatted_val = f"{obj.avg_flowrate:.2f}"
            return format_html(
                '<span style="color: #3B82F6;">{}</span> m³/h',
                formatted_val
            )
        return '-'
    avg_flowrate_display.short_description = 'Avg Flowrate'
    
    def avg_pressure_display(self, obj):
        """Display average pressure"""
        if obj.avg_pressure is not None:
            # FIXED: Format number first
            formatted_val = f"{obj.avg_pressure:.2f}"
            return format_html(
                '<span style="color: #10B981;">{}</span> bar',
                formatted_val
            )
        return '-'
    avg_pressure_display.short_description = 'Avg Pressure'
    
    def avg_temperature_display(self, obj):
        """Display average temperature"""
        if obj.avg_temperature is not None:
            # FIXED: Format number first
            formatted_val = f"{obj.avg_temperature:.2f}"
            return format_html(
                '<span style="color: #F59E0B;">{}</span> °C',
                formatted_val
            )
        return '-'
    avg_temperature_display.short_description = 'Avg Temperature'
    
    def outlier_count_display(self, obj):
        """Display outlier count with warning icon"""
        count = getattr(obj, '_outlier_count', 0)
        if count > 0:
            return format_html(
                '<span style="background: #FEE2E2; color: #DC2626; padding: 3px 8px; '
                'border-radius: 4px; font-weight: bold;">⚠️ {}</span>',
                count
            )
        # FIXED: Use mark_safe because format_html requires arguments
        return mark_safe(
            '<span style="color: #10B981;">✓ None</span>'
        )
    outlier_count_display.short_description = 'Outliers'
    
    def actions_display(self, obj):
        """Display action buttons"""
        view_url = reverse('admin:api_dataset_change', args=[obj.id])
        return format_html(
            '<a href="{}" style="background: #3B82F6; color: white; padding: 4px 12px; '
            'border-radius: 4px; text-decoration: none; font-size: 12px;">View Details</a>',
            view_url
        )
    actions_display.short_description = 'Actions'
    
    def equipment_preview(self, obj):
        """Display first 5 equipment items"""
        equipment = obj.equipment.all()[:5]
        if not equipment:
            return "No equipment data"
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #F3F4F6; font-weight: bold;">'
        html += '<th style="padding: 8px; text-align: left; border: 1px solid #E5E7EB;">Name</th>'
        html += '<th style="padding: 8px; text-align: left; border: 1px solid #E5E7EB;">Type</th>'
        html += '<th style="padding: 8px; text-align: right; border: 1px solid #E5E7EB;">Flowrate</th>'
        html += '<th style="padding: 8px; text-align: right; border: 1px solid #E5E7EB;">Pressure</th>'
        html += '<th style="padding: 8px; text-align: right; border: 1px solid #E5E7EB;">Temp</th>'
        html += '</tr>'
        
        for eq in equipment:
            html += '<tr>'
            html += f'<td style="padding: 8px; border: 1px solid #E5E7EB;">{eq.equipment_name}</td>'
            html += f'<td style="padding: 8px; border: 1px solid #E5E7EB;">{eq.equipment_type}</td>'
            html += f'<td style="padding: 8px; text-align: right; border: 1px solid #E5E7EB;">{eq.flowrate:.2f}</td>'
            html += f'<td style="padding: 8px; text-align: right; border: 1px solid #E5E7EB;">{eq.pressure:.2f}</td>'
            html += f'<td style="padding: 8px; text-align: right; border: 1px solid #E5E7EB;">{eq.temperature:.2f}</td>'
            html += '</tr>'
        
        html += '</table>'
        html += f'<p style="margin-top: 10px; color: #6B7280;">Showing 5 of {obj.total_equipment} equipment</p>'
        
        # FIXED: Use mark_safe instead of format_html for generated HTML strings
        return mark_safe(html)
    equipment_preview.short_description = 'Equipment Data Preview'
    
    def export_selected_csv(self, request, queryset):
        """Export selected datasets as CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="datasets_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Dataset', 'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        
        for dataset in queryset:
            for eq in dataset.equipment.all():
                writer.writerow([
                    dataset.filename,
                    eq.equipment_name,
                    eq.equipment_type,
                    eq.flowrate,
                    eq.pressure,
                    eq.temperature
                ])
        
        self.message_user(request, f"Exported {queryset.count()} datasets")
        return response
    export_selected_csv.short_description = "📥 Export selected as CSV"
    
    def delete_with_equipment(self, request, queryset):
        """Delete datasets and all related equipment"""
        count = queryset.count()
        equipment_count = sum(d.total_equipment for d in queryset)
        queryset.delete()
        self.message_user(
            request,
            f"Deleted {count} datasets and {equipment_count} equipment records"
        )
    delete_with_equipment.short_description = "🗑️ Delete with equipment"
    
    def recalculate_stats(self, request, queryset):
        """Recalculate statistics for selected datasets"""
        for dataset in queryset:
            equipment = dataset.equipment.all()
            if equipment:
                dataset.avg_flowrate = sum(e.flowrate for e in equipment) / len(equipment)
                dataset.avg_pressure = sum(e.pressure for e in equipment) / len(equipment)
                dataset.avg_temperature = sum(e.temperature for e in equipment) / len(equipment)
                dataset.save()
        
        self.message_user(request, f"Recalculated stats for {queryset.count()} datasets")
    recalculate_stats.short_description = "🔄 Recalculate statistics"


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Enhanced Equipment admin with inline editing"""
    
    list_display = [
        'equipment_name',
        'equipment_type',
        'dataset_link',
        'flowrate_display',
        'pressure_display',
        'temperature_display',
        'outlier_status_display'
    ]
    
    list_filter = [
        'equipment_type',
        'is_pressure_outlier',
        'is_temperature_outlier',
        'dataset'
    ]
    
    search_fields = ['equipment_name', 'equipment_type', 'dataset__filename']
    
    list_editable = ['equipment_type']  # Allow inline editing
    
    fieldsets = (
        ('Equipment Information', {
            'fields': ('equipment_name', 'equipment_type', 'dataset')
        }),
        ('Parameters', {
            'fields': ('flowrate', 'pressure', 'temperature')
        }),
        ('Outlier Detection', {
            'fields': ('is_pressure_outlier', 'is_temperature_outlier'),
            'classes': ('collapse',)
        })
    )
    
    def dataset_link(self, obj):
        """Link to parent dataset"""
        url = reverse('admin:api_dataset_change', args=[obj.dataset.id])
        return format_html(
            '<a href="{}" style="color: #3B82F6;">📄 {}</a>',
            url, obj.dataset.filename
        )
    dataset_link.short_description = 'Dataset'
    
    def flowrate_display(self, obj):
        """Display flowrate with color"""
        # FIXED: Format number first
        formatted_val = f"{obj.flowrate:.2f}"
        return format_html(
            '<span style="color: #3B82F6; font-weight: bold;">{}</span>',
            formatted_val
        )
    flowrate_display.short_description = 'Flowrate (m³/h)'
    flowrate_display.admin_order_field = 'flowrate'
    
    def pressure_display(self, obj):
        """Display pressure with outlier indicator"""
        color = '#EF4444' if obj.is_pressure_outlier else '#10B981'
        icon = '⚠️' if obj.is_pressure_outlier else ''
        # FIXED: Format number first
        formatted_val = f"{obj.pressure:.2f}"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, formatted_val
        )
    pressure_display.short_description = 'Pressure (bar)'
    pressure_display.admin_order_field = 'pressure'
    
    def temperature_display(self, obj):
        """Display temperature with outlier indicator"""
        color = '#EF4444' if obj.is_temperature_outlier else '#F59E0B'
        icon = '⚠️' if obj.is_temperature_outlier else ''
        # FIXED: Format number first
        formatted_val = f"{obj.temperature:.2f}"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, formatted_val
        )
    temperature_display.short_description = 'Temperature (°C)'
    temperature_display.admin_order_field = 'temperature'
    
    def outlier_status_display(self, obj):
        """Display outlier status badge"""
        if obj.is_pressure_outlier or obj.is_temperature_outlier:
            # FIXED: Use mark_safe because format_html requires arguments
            return mark_safe(
                '<span style="background: #FEE2E2; color: #DC2626; padding: 3px 8px; '
                'border-radius: 4px; font-weight: bold;">⚠️ OUTLIER</span>'
            )
        # FIXED: Use mark_safe
        return mark_safe(
            '<span style="background: #D1FAE5; color: #065F46; padding: 3px 8px; '
            'border-radius: 4px; font-weight: bold;">✓ NORMAL</span>'
        )
    outlier_status_display.short_description = 'Status'


# Customize admin site header
admin.site.site_header = "Chemical Equipment Parameter Visualizer - Admin Portal"
admin.site.site_title = "CEPV Admin"
admin.site.index_title = "Dataset & Equipment Management"