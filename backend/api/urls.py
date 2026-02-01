from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    DatasetViewSet,
    EquipmentViewSet,
    CSVUploadView,
    health_check,
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
    
    # CSV Upload
    path('upload/', CSVUploadView.as_view(), name='csv-upload'),
    
    # Router URLs (datasets, equipment)
    path('', include(router.urls)),
]