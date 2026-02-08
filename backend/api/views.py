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


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Equipment listing (read-only)."""
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by dataset_id if provided."""
        queryset = Equipment.objects.select_related('dataset')
        dataset_id = self.request.query_params.get('dataset_id')
        
        if dataset_id:
            queryset = queryset.filter(dataset_id=dataset_id)
        
        return queryset


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