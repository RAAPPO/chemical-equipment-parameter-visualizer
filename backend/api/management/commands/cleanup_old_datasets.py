"""
Custom management command to clean up old datasets.
Run: python manage.py cleanup_old_datasets
"""
from django.core.management.base import BaseCommand
from api.models import Dataset


class Command(BaseCommand):
    help = 'Remove old datasets beyond the FIFO limit'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Number of datasets to keep (default: 5)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
    
    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        
        datasets_to_keep = Dataset.objects.order_by('-uploaded_at')[:limit]
        datasets_to_delete = Dataset.objects.exclude(
            id__in=[d.id for d in datasets_to_keep]
        )
        
        count = datasets_to_delete.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No datasets to delete'))
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'Would delete {count} dataset(s):')
            )
            for dataset in datasets_to_delete:
                self.stdout.write(f'  - {dataset.filename} ({dataset.uploaded_at})')
        else:
            datasets_to_delete.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {count} dataset(s)')
            )
