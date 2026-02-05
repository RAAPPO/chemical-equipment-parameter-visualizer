"""
API Views - Clean, delegating to service layer.
Industry pattern: Views handle HTTP, Services handle logic.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse
import logging

from .models import Dataset, Equipment
from .serializers import (
    DatasetSerializer,
    DatasetListSerializer,
    EquipmentSerializer,
    AnalyticsSerializer,
)
from .services import DatasetService, CSVValidationError
from .pdf_generator import generate_dataset_pdf

logger = logging.getLogger(__name__)


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Dataset listing and retrieval.
    Read-only because creation is via CSV upload endpoint.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Optimize query with prefetch."""
        return Dataset.objects.with_equipment_count().prefetch_related('equipment')
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list':
            return DatasetListSerializer
        return DatasetSerializer
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for a specific dataset."""
        try:
            analytics_data = DatasetService.get_analytics(pk)
            serializer = AnalyticsSerializer(analytics_data)
            return Response(serializer.data)
        except ValueError as e:
            logger.warning(f"Analytics request failed: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error in analytics: {e}", exc_info=True)
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CSVUploadView(APIView):
    """CSV file upload endpoint with validation."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Handle CSV file upload."""
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        filename = file.name
        
        if not filename.lower().endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            dataset = DatasetService.create_dataset_from_csv(file, filename)
            serializer = DatasetSerializer(dataset)
            
            logger.info(f"CSV uploaded successfully: {filename} by user {request.user.username}")
            
            return Response(
                {
                    'message': 'CSV uploaded successfully',
                    'dataset': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        except CSVValidationError as e:
            logger.warning(f"CSV validation failed for {filename}: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error during CSV upload: {e}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EquipmentViewSet(viewsets.ModelViewSet):  # Changed to ModelViewSet
    """ViewSet for Equipment listing, updating, and deleting."""
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by dataset_id if provided."""
        queryset = Equipment.objects.select_related('dataset')
        dataset_id = self.request.query_params.get('dataset_id')
        
        if dataset_id:
            queryset = queryset.filter(dataset_id=dataset_id)
        
        return queryset

    def update(self, request, *args, **kwargs):
        """Update equipment parameters"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Recalculate dataset statistics
        dataset = instance.dataset
        equipment_list = dataset.equipment.all()
        if equipment_list:
            dataset.avg_flowrate = sum(e.flowrate for e in equipment_list) / len(equipment_list)
            dataset.avg_pressure = sum(e.pressure for e in equipment_list) / len(equipment_list)
            dataset.avg_temperature = sum(e.temperature for e in equipment_list) / len(equipment_list)
            dataset.save()
        
        logger.info(f"Equipment {instance.id} updated by {request.user.username}")
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete equipment and recalculate dataset stats"""
        instance = self.get_object()
        dataset = instance.dataset
        
        # Delete equipment
        instance.delete()
        
        # Recalculate dataset statistics
        equipment_list = dataset.equipment.all()
        if equipment_list:
            dataset.total_equipment = len(equipment_list)
            dataset.avg_flowrate = sum(e.flowrate for e in equipment_list) / len(equipment_list)
            dataset.avg_pressure = sum(e.pressure for e in equipment_list) / len(equipment_list)
            dataset.avg_temperature = sum(e.temperature for e in equipment_list) / len(equipment_list)
            dataset.save()
        else:
            # If no equipment left, reset stats
            dataset.total_equipment = 0
            dataset.avg_flowrate = None
            dataset.avg_pressure = None
            dataset.avg_temperature = None
            dataset.save()
        
        logger.info(f"Equipment {instance.id} deleted by {request.user.username}")
        
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_dataset_pdf(request, dataset_id):
    """Download PDF report for a dataset."""
    try:
        pdf_buffer = generate_dataset_pdf(dataset_id)
        dataset = Dataset.objects.get(id=dataset_id)
        filename = f"report_{dataset.filename.replace('.csv', '')}.pdf"
        
        response = FileResponse(
            pdf_buffer,
            content_type='application/pdf',
            as_attachment=True,
            filename=filename
        )
        
        logger.info(f"PDF generated for dataset {dataset_id} by user {request.user.username}")
        return response
    
    except Dataset.DoesNotExist:
        logger.warning(f"PDF request for non-existent dataset: {dataset_id}")
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        return Response(
            {'error': 'PDF generation failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint (public)."""
    return Response({
        'status': 'healthy',
        'message': 'Chemical Equipment Parameter Visualizer API',
        'version': '1.0.0'
    })

# --- ADDED REGISTRATION LOGIC ---
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    User registration endpoint.
    Public access (no authentication required).
    """
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    
    # Validation
    if not username or len(username) < 3:
        return Response(
            {'error': 'Username must be at least 3 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not email or '@' not in email:
        return Response(
            {'error': 'Valid email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not password or len(password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if username exists
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already taken'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if email exists
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already registered'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )
        
        logger.info(f"New user registered: {username}")
        
        return Response({
            'message': 'Registration successful',
            'username': username,
            'email': email
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return Response(
            {'error': 'Registration failed. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )