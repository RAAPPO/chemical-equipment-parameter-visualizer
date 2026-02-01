"""
Chemical Equipment Parameter Visualizer - Data Models
Industry-standard Django models with optimizations and managers.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class DatasetManager(models.Manager):
    """Custom manager for Dataset model with optimized queries."""
    
    def with_equipment_count(self):
        """Annotate datasets with equipment count."""
        from django.db.models import Count
        return self.annotate(equipment_count=Count('equipment'))
    
    def recent(self, limit=5):
        """Get recent datasets with equipment prefetched."""
        return self.prefetch_related('equipment').order_by('-uploaded_at')[:limit]


class Dataset(models.Model):
    """Metadata for uploaded CSV datasets with FIFO management."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    total_equipment = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    
    objects = DatasetManager()
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['-uploaded_at']),
            models.Index(fields=['filename']),
        ]
        verbose_name = "Dataset"
        verbose_name_plural = "Datasets"
    
    def __str__(self):
        return f"{self.filename} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_analytics(self):
        """Calculate analytics for this dataset using database aggregation."""
        from django.db.models import Count, Q
        
        equipment_qs = self.equipment.all()
        
        # Calculate type distribution using aggregation
        type_distribution = dict(
            equipment_qs.values('equipment_type')
            .annotate(count=Count('id'))
            .values_list('equipment_type', 'count')
        )
        
        # Get outliers efficiently (optimized by the Equipment composite index)
        outliers = equipment_qs.filter(
            Q(is_pressure_outlier=True) | Q(is_temperature_outlier=True)
        ).values('equipment_name', 'equipment_type', 'is_pressure_outlier', 'is_temperature_outlier')
        
        return {
            'total_equipment': self.total_equipment,
            'avg_flowrate': self.avg_flowrate,
            'avg_pressure': self.avg_pressure,
            'avg_temperature': self.avg_temperature,
            'equipment_type_distribution': type_distribution,
            'outliers_count': len(outliers),
            'outlier_equipment': [
                {
                    'name': eq['equipment_name'],
                    'type': eq['equipment_type'],
                    'pressure_outlier': eq['is_pressure_outlier'],
                    'temperature_outlier': eq['is_temperature_outlier'],
                }
                for eq in outliers
            ]
        }


class Equipment(models.Model):
    """Individual equipment records from CSV datasets."""
    
    class EquipmentType(models.TextChoices):
        PUMP = 'Pump', 'Pump'
        COMPRESSOR = 'Compressor', 'Compressor'
        VALVE = 'Valve', 'Valve'
        HEAT_EXCHANGER = 'HeatExchanger', 'Heat Exchanger'
        REACTOR = 'Reactor', 'Reactor'
        CONDENSER = 'Condenser', 'Condenser'
        TANK = 'Tank', 'Tank'
        OTHER = 'Other', 'Other'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='equipment',
        db_index=True
    )
    equipment_name = models.CharField(max_length=255, db_index=True)
    equipment_type = models.CharField(
        max_length=50,
        choices=EquipmentType.choices,
        db_index=True
    )
    flowrate = models.FloatField(validators=[MinValueValidator(0)])
    pressure = models.FloatField(validators=[MinValueValidator(0)])
    temperature = models.FloatField()
    
    is_pressure_outlier = models.BooleanField(default=False, db_index=True)
    is_temperature_outlier = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        ordering = ['equipment_name']
        indexes = [
            models.Index(fields=['dataset_id', 'equipment_type']),
            models.Index(fields=['equipment_name']),
            # Composite index for efficient outlier filtering
            models.Index(fields=['dataset_id', 'is_pressure_outlier', 'is_temperature_outlier']),
        ]
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"

    @property
    def is_outlier(self):
        """Check if equipment has any outlier flags. Used by Admin and Serializers."""
        return self.is_pressure_outlier or self.is_temperature_outlier


@receiver(post_save, sender=Dataset)
def maintain_dataset_limit(sender, instance, created, **kwargs):
    """Maintain FIFO limit of 5 datasets."""
    if created:
        datasets_to_keep = Dataset.objects.order_by('-uploaded_at')[:5].values_list('id', flat=True)
        Dataset.objects.exclude(id__in=list(datasets_to_keep)).delete()