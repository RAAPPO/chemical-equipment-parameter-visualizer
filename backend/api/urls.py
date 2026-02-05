from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    DatasetViewSet,
    EquipmentViewSet,
    CSVUploadView,
    health_check,
    download_dataset_pdf,
    register_user,  # <-- Added this import
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')
router.register(r'equipment', EquipmentViewSet, basename='equipment')

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),
    
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', register_user, name='register'),
    
    # CSV Upload
    path('upload/', CSVUploadView.as_view(), name='csv-upload'),
    
    # PDF Download 
    path('datasets/<uuid:dataset_id>/pdf/', download_dataset_pdf, name='dataset-pdf'),

    # Router URLs (datasets, equipment)
    path('', include(router.urls)),
]