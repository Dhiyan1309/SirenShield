from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.voice_monitor import start_voice_monitoring_for_user, stop_voice_monitoring
import time

class Command(BaseCommand):
    help = 'Test the voice monitoring system'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to test with')
        parser.add_argument('--duration', type=int, default=60, help='Duration to monitor in seconds')

    def handle(self, *args, **options):
        username = options['username']
        duration = options['duration']
        
        if not username:
            self.stdout.write(self.style.ERROR('Please provide a username with --username'))
            return
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Starting voice monitoring for user: {username}'))
        self.stdout.write(f'Monitoring for {duration} seconds. Say "help me" to test emergency detection.')
        
        # Start monitoring
        start_voice_monitoring_for_user(user)
        
        try:
            # Monitor for specified duration
            time.sleep(duration)
        except KeyboardInterrupt:
            self.stdout.write('\nStopping voice monitoring...')
        finally:
            # Stop monitoring
            stop_voice_monitoring()
            self.stdout.write(self.style.SUCCESS('Voice monitoring stopped')) 