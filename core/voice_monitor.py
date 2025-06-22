import speech_recognition as sr
import pyaudio
import wave
import threading
import time
import os
import tempfile
import requests
from django.conf import settings
from django.core.mail import send_mail
from .models import UserProfile, EmergencyContact, SafetySession, EmergencyAlert
from datetime import datetime

class VoiceMonitor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_monitoring = False
        self.emergency_phrase = "help me"
        self.monitor_thread = None
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def start_monitoring(self, user):
        """Start monitoring voice for emergency phrases"""
        if self.is_monitoring:
            return False
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_voice, args=(user,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print(f"Voice monitoring started for user: {user.username}")
        return True
    
    def stop_monitoring(self):
        """Stop voice monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("Voice monitoring stopped")
    
    def _monitor_voice(self, user):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Listen for audio input
                with self.microphone as source:
                    print("Listening for voice input...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                # Try to recognize speech
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Recognized: {text}")
                    
                    # Check for emergency phrase
                    if self.emergency_phrase in text:
                        print(f"Emergency phrase detected: {text}")
                        self._handle_emergency(user, text)
                    
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results: {e}")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in voice monitoring: {e}")
                time.sleep(2)
    
    def _get_user_location(self):
        """Get user's current location using IP geolocation"""
        try:
            # Get location from IP
            print("Attempting to get location from IP...")
            response = requests.get('https://ipapi.co/json/', timeout=10)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response data: {data}")
                
                location_info = {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'city': data.get('city', 'Unknown'),
                    'country': data.get('country_name', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'postal': data.get('postal', ''),
                    'timezone': data.get('timezone', 'Unknown'),
                    'accuracy': 'IP-based (approximate)'
                }
                
                if location_info['latitude'] and location_info['longitude']:
                    print(f"Location detected: {location_info['city']}, {location_info['country']} at {location_info['latitude']}, {location_info['longitude']}")
                    return location_info
                else:
                    print("No latitude/longitude in response")
                    return self._get_fallback_location()
            else:
                print(f"Failed to get location, status code: {response.status_code}")
                return self._get_fallback_location()
                
        except Exception as e:
            print(f"Error getting location: {e}")
            return self._get_fallback_location()
    
    def _get_fallback_location(self):
        """Get fallback location data"""
        print("Using fallback location data")
        return {
            'latitude': 28.6139,  # Default to Delhi coordinates
            'longitude': 77.2090,
            'city': 'Delhi',
            'country': 'India',
            'region': 'Delhi',
            'postal': '',
            'timezone': 'Asia/Kolkata',
            'accuracy': 'Fallback (default)'
        }
    
    def _find_nearby_police_stations(self, lat, lon):
        """Find nearby police stations using OpenStreetMap API"""
        try:
            # Overpass API query for police stations within 5km
            query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="police"](around:5000,{lat},{lon});
            );
            out body;
            >;
            out skel qt;
            """
            
            response = requests.get(
                'https://overpass-api.de/api/interpreter',
                params={'data': query}
            )
            
            if response.status_code == 200:
                data = response.json()
                stations = []
                
                for element in data.get('elements', []):
                    station = {
                        'id': element.get('id'),
                        'lat': element.get('lat'),
                        'lon': element.get('lon'),
                        'name': element.get('tags', {}).get('name', 'Police Station'),
                        'address': element.get('tags', {}).get('addr:street', ''),
                        'phone': element.get('tags', {}).get('phone', ''),
                        'distance': self._calculate_distance(lat, lon, element.get('lat'), element.get('lon'))
                    }
                    stations.append(station)
                
                # Sort by distance
                stations.sort(key=lambda x: x['distance'])
                return stations[:5]  # Return top 5 nearest stations
            
        except Exception as e:
            print(f"Error finding police stations: {e}")
        
        return []
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _handle_emergency(self, user, detected_text):
        """Handle emergency situation"""
        try:
            # Check if user has active safety session
            active_session = SafetySession.objects.filter(
                user=user,
                is_active=True
            ).first()
            
            if not active_session:
                print("No active safety session found")
                return
            
            # Get user's location
            location_data = self._get_user_location()
            location_str = ""
            
            if location_data:
                lat = location_data['latitude']
                lon = location_data['longitude']
                location_str = f"{lat},{lon}"
                
                # Find nearby police stations
                police_stations = self._find_nearby_police_stations(lat, lon)
                print(f"Found {len(police_stations)} nearby police stations")
                
                # Create Google Maps links
                user_maps_link = f"https://maps.google.com/?q={lat},{lon}"
                nearest_police_maps_link = ""
                if police_stations:
                    nearest_police_maps_link = f"https://maps.google.com/?q={police_stations[0]['lat']},{police_stations[0]['lon']}"
                
                # Create emergency alert with detailed location
                alert = EmergencyAlert.objects.create(
                    safety_session=active_session,
                    alert_type='voice',
                    location=location_str,
                    description=f"Emergency phrase detected: '{detected_text}'. Location: {location_data['city']}, {location_data['country']}. Coordinates: {lat}, {lon}",
                    shown_to_user=False
                )
                
                # Get user's emergency contacts
                try:
                    user_profile = user.userprofile
                    emergency_contacts = user_profile.emergency_contacts.all()
                    
                    if emergency_contacts:
                        # Send email alerts with location and police stations
                        for contact in emergency_contacts:
                            self._send_emergency_email(contact, user, detected_text, location_data, police_stations, user_maps_link, nearest_police_maps_link)
                        
                        print(f"Emergency alerts sent to {len(emergency_contacts)} contacts")
                        
                        # Print police station information
                        if police_stations:
                            print("\n=== NEARBY POLICE STATIONS ===")
                            for i, station in enumerate(police_stations, 1):
                                print(f"{i}. {station['name']}")
                                print(f"   Address: {station['address']}")
                                print(f"   Phone: {station['phone']}")
                                print(f"   Distance: {station['distance']:.2f} km")
                                print(f"   Map: https://maps.google.com/?q={station['lat']},{station['lon']}")
                                print()
                            
                            # Print navigation instruction
                            if nearest_police_maps_link:
                                print(f"🚨 EMERGENCY: Navigate to nearest police station: {nearest_police_maps_link}")
                        else:
                            print("No nearby police stations found")
                    else:
                        print("No emergency contacts found")
                        
                except UserProfile.DoesNotExist:
                    print("User profile not found")
            else:
                # Create alert without location
                alert = EmergencyAlert.objects.create(
                    safety_session=active_session,
                    alert_type='voice',
                    location='',
                    description=f"Emergency phrase detected: '{detected_text}'. Location unavailable.",
                    shown_to_user=False
                )
                
                # Send alerts without location
                try:
                    user_profile = user.userprofile
                    emergency_contacts = user_profile.emergency_contacts.all()
                    
                    if emergency_contacts:
                        for contact in emergency_contacts:
                            self._send_emergency_email(contact, user, detected_text, None, [], "", "")
                        
                        print(f"Emergency alerts sent to {len(emergency_contacts)} contacts (no location)")
                    else:
                        print("No emergency contacts found")
                        
                except UserProfile.DoesNotExist:
                    print("User profile not found")
            
        except Exception as e:
            print(f"Error handling emergency: {e}")
    
    def _send_emergency_email(self, contact, user, detected_text, location_data=None, police_stations=None, user_maps_link="", nearest_police_maps_link=""):
        """Send emergency email to contact"""
        try:
            # Use the same subject and message as manual emergency alert
            lat = location_data['latitude'] if location_data and 'latitude' in location_data else None
            lng = location_data['longitude'] if location_data and 'longitude' in location_data else None
            map_link = f"https://maps.google.com/?q={lat},{lng}" if lat and lng else "Location not available"
            location_details = f"Latitude: {lat}, Longitude: {lng}\nGoogle Maps: {map_link}" if lat and lng else "Location not available"

            subject = f"EMERGENCY ALERT: {user.get_full_name()} needs help!"
            message = (
                f"EMERGENCY ALERT from {user.get_full_name()}!\n"
                f"Location: {location_details}\n"
                f"Description: {detected_text}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"\nPlease respond immediately!"
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [contact.email],
                fail_silently=False,
            )
            print(f"Emergency email sent to {contact.email}")
        except Exception as e:
            print(f"Error sending emergency email: {e}")

# Global voice monitor instance
voice_monitor = VoiceMonitor()

def start_voice_monitoring_for_user(user):
    """Start voice monitoring for a specific user"""
    return voice_monitor.start_monitoring(user)

def stop_voice_monitoring():
    """Stop voice monitoring"""
    voice_monitor.stop_monitoring()

def is_monitoring_active():
    """Check if voice monitoring is active"""
    return voice_monitor.is_monitoring 