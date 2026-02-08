from django.contrib.auth.models import User
from .models import Dataset, Equipment
from django.db.models import Q

def admin_stats(request):
    """Provide stats for admin dashboard"""
    if not request.path.startswith('/admin/'):
        return {}
    
    try:
        from django.contrib.auth.models import User
        dataset_count = Dataset.objects.count()
        equipment_count = Equipment.objects.count()
        user_count = User.objects.count()
        outlier_count = Equipment.objects.filter(
            Q(is_pressure_outlier=True) | Q(is_temperature_outlier=True)
        ).count()
        recent_datasets = Dataset.objects.order_by('-uploaded_at')[:5]
        
        return {
            'dataset_count': dataset_count,
            'equipment_count': equipment_count,
            'user_count': user_count,
            'outlier_count': outlier_count,
            'recent_datasets': recent_datasets,
        }
    except Exception:
        return {}