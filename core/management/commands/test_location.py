from django.core.management.base import BaseCommand
from core.voice_monitor import VoiceMonitor

class Command(BaseCommand):
    help = 'Test the location detection functionality'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing location detection...'))
        
        monitor = VoiceMonitor()
        
        # Test location detection
        location = monitor._get_user_location()
        
        if location:
            self.stdout.write(self.style.SUCCESS(f'Location detected successfully:'))
            self.stdout.write(f'  City: {location["city"]}')
            self.stdout.write(f'  Country: {location["country"]}')
            self.stdout.write(f'  Latitude: {location["latitude"]}')
            self.stdout.write(f'  Longitude: {location["longitude"]}')
            self.stdout.write(f'  Accuracy: {location["accuracy"]}')
            
            # Test police station detection
            self.stdout.write(self.style.SUCCESS('\nTesting police station detection...'))
            police_stations = monitor._find_nearby_police_stations(location['latitude'], location['longitude'])
            
            if police_stations:
                self.stdout.write(f'Found {len(police_stations)} nearby police stations:')
                for i, station in enumerate(police_stations[:3], 1):
                    self.stdout.write(f'  {i}. {station["name"]}')
                    self.stdout.write(f'     Address: {station["address"]}')
                    self.stdout.write(f'     Distance: {station["distance"]:.2f} km')
                    self.stdout.write(f'     Map: https://maps.google.com/?q={station["lat"]},{station["lon"]}')
            else:
                self.stdout.write(self.style.WARNING('No nearby police stations found'))
        else:
            self.stdout.write(self.style.ERROR('Failed to detect location')) 