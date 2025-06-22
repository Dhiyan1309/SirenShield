from django.core.management.base import BaseCommand
from core.models import EmergencyAlert

class Command(BaseCommand):
    help = 'Reset all existing emergency alerts to shown_to_user=True'

    def handle(self, *args, **options):
        # Update all existing alerts to be marked as shown
        updated_count = EmergencyAlert.objects.filter(shown_to_user=False).update(shown_to_user=True)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully marked {updated_count} emergency alerts as shown')
        ) 