from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Dataset, Equipment
from .serializers import (
    DatasetSerializer,
    DatasetListSerializer,
    EquipmentSerializer,
    AnalyticsSerializer,
)
from .utils import process_csv_and_create_dataset, get_analytics_for_dataset
from .pdf_generator import generate_dataset_pdf

class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Dataset CRUD operations.
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list':
            return DatasetListSerializer
        return DatasetSerializer

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for a specific dataset."""
        try:
            analytics_data = get_analytics_for_dataset(pk)
            serializer = AnalyticsSerializer(analytics_data)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )


class CSVUploadView(APIView):
    """
    API endpoint for CSV file upload.
    """
    parser_classes = [MultiPartParser, FormParser]
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

        # Validate file extension
        if not filename.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Process CSV and create dataset
            dataset = process_csv_and_create_dataset(file, filename)
            serializer = DatasetSerializer(dataset)
            
            return Response(
                {
                    'message': 'CSV uploaded successfully',
                    'dataset': serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Equipment (read-only).
    """
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter equipment by dataset_id if provided."""
        queryset = Equipment.objects.all()
        dataset_id = self.request.query_params.get('dataset_id', None)
        if dataset_id:
            queryset = queryset.filter(dataset_id=dataset_id)
        return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint (public)."""
    return Response({
        'status': 'healthy',
        'message': 'Chemical Equipment Parameter Visualizer API is running',
        'version': '1.0.0'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_dataset_pdf(request, dataset_id):
    """Download PDF report for a dataset."""
    try:
        pdf_buffer = generate_dataset_pdf(dataset_id)
        
        # Get dataset filename
        dataset = Dataset.objects.get(id=dataset_id)
        filename = f"report_{dataset.filename.replace('.csv', '')}.pdf"
        
        response = FileResponse(
            pdf_buffer,
            content_type='application/pdf',
            as_attachment=True,
            filename=filename
        )
        
        return response
    
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'PDF generation failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )