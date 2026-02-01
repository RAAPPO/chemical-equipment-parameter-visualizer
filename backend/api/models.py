from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Dataset(models.Model):
    """
    Stores metadata for each uploaded CSV dataset.
    Only the last 5 datasets are retained (FIFO logic via signal).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_equipment = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class Equipment(models.Model):
    """
    Stores individual equipment records from the CSV.
    Linked to a Dataset via foreign key.
    """
    EQUIPMENT_TYPES = [
        ('Pump', 'Pump'),
        ('Compressor', 'Compressor'),
        ('Valve', 'Valve'),
        ('HeatExchanger', 'HeatExchanger'),
        ('Reactor', 'Reactor'),
        ('Condenser', 'Condenser'),
        ('Tank', 'Tank'),
        ('Other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=50, choices=EQUIPMENT_TYPES)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    
    # Outlier detection flags (Z-score > 2)
    is_pressure_outlier = models.BooleanField(default=False)
    is_temperature_outlier = models.BooleanField(default=False)

    class Meta:
        ordering = ['equipment_name']

    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"


@receiver(post_save, sender=Dataset)
def maintain_dataset_limit(sender, instance, created, **kwargs):
    """
    Signal to maintain only the last 5 datasets.
    Deletes older datasets automatically (FIFO).
    """
    if created:
        # Keep only the 5 most recent datasets
        datasets_to_keep = Dataset.objects.order_by('-uploaded_at')[:5]
        Dataset.objects.exclude(id__in=[d.id for d in datasets_to_keep]).delete()