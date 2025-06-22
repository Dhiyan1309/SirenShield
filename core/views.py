from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, datetime
import json
import os
import tempfile
from .voice_detection import VoiceSpeechDetector
from .voice_monitor import start_voice_monitoring_for_user, stop_voice_monitoring, is_monitoring_active
from .models import UserProfile, EmergencyContact, SafetySession, EmergencyAlert, Alert
from .forms import UserRegistrationForm, UserProfileForm, EmergencyContactForm, SafetyModeForm
import requests
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def home(request):
    return render(request, 'core/home.html')

@login_required
def profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    emergency_contacts = EmergencyContact.objects.filter(user_profiles=profile)
    
    if request.method == 'POST':
        # Update user data
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        
        # Update profile data
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.sms_notifications = request.POST.get('sms_notifications') == 'on'
        profile.push_notifications = request.POST.get('push_notifications') == 'on'
        
        # Handle profile image
        if 'profile_image' in request.FILES:
            # Delete old profile image if exists
            if profile.profile_image:
                default_storage.delete(profile.profile_image.path)
            profile.profile_image = request.FILES['profile_image']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'profile': profile,
        'emergency_contacts': emergency_contacts,
    }
    return render(request, 'core/profile.html', context)

@login_required
def guardian_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    emergency_contacts = EmergencyContact.objects.filter(user_profiles=profile)
    
    if request.method == 'POST':
        # Update user data
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update profile data
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')
        profile.role = request.POST.get('role', 'Guardian')
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.sms_notifications = request.POST.get('sms_notifications') == 'on'
        profile.push_notifications = request.POST.get('push_notifications') == 'on'
        
        # Handle profile image
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
        
        profile.save()
        
        # Handle emergency contacts
        contact_ids = request.POST.getlist('emergency_contacts')
        profile.emergency_contacts.set(contact_ids)
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('guardian_profile')
    
    context = {
        'profile': profile,
        'emergency_contacts': emergency_contacts,
    }
    return render(request, 'core/guardian_profile.html', context)

@login_required
def add_emergency_contact(request):
    if request.method == 'POST':
        try:
            contact = EmergencyContact.objects.create(
                name=request.POST.get('name'),
                relationship=request.POST.get('relationship'),
                phone_number=request.POST.get('phone'),
                email=request.POST.get('email', ''),
                address=request.POST.get('address', '')
            )
            request.user.userprofile.emergency_contacts.add(contact)
            messages.success(request, 'Emergency contact added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding contact: {str(e)}')
    
    return redirect('guardian_profile')

@login_required
def edit_emergency_contact(request):
    if request.method == 'POST':
        contact_id = request.POST.get('contact_id')
        contact = get_object_or_404(EmergencyContact, id=contact_id)
        
        try:
            contact.name = request.POST.get('name')
            contact.relationship = request.POST.get('relationship')
            contact.phone_number = request.POST.get('phone')
            contact.email = request.POST.get('email', '')
            contact.address = request.POST.get('address', '')
            contact.save()
            messages.success(request, 'Contact updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating contact: {str(e)}')
    
    return redirect('guardian_profile')

@login_required
def delete_emergency_contact(request, contact_id):
    if request.method == 'POST':
        contact = get_object_or_404(EmergencyContact, id=contact_id)
        request.user.userprofile.emergency_contacts.remove(contact)
        contact.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_contact_details(request, contact_id):
    contact = get_object_or_404(EmergencyContact, id=contact_id)
    data = {
        'name': contact.name,
        'relationship': contact.relationship,
        'phone': contact.phone_number,
        'email': contact.email,
        'address': contact.address
    }
    return JsonResponse(data)

@login_required
def update_notification_preferences(request):
    if request.method == 'POST':
        user_profile = request.user.userprofile
        user_profile.email_notifications = 'email_notifications' in request.POST
        user_profile.sms_notifications = 'sms_notifications' in request.POST
        user_profile.push_notifications = 'push_notifications' in request.POST
        user_profile.save()
        messages.success(request, 'Notification preferences updated successfully!')
    return redirect('guardian_profile')

@login_required
def safety_mode(request):
    if request.method == 'POST':
        # Create a new safety session
        session = SafetySession.objects.create(
            user=request.user,
            is_active=True
        )
        
        # Update user profile
        profile = request.user.userprofile
        profile.is_safety_mode_active = True
        profile.last_safety_mode_activation = timezone.now()
        profile.save()
        
        # Start voice monitoring
        try:
            start_voice_monitoring_for_user(request.user)
            messages.success(request, 'Safety mode activated! Voice monitoring started.')
        except Exception as e:
            messages.warning(request, f'Safety mode activated but voice monitoring failed: {str(e)}')
        
        return redirect('safety_dashboard')
    
    return render(request, 'core/safety_mode.html')

@login_required
def safety_dashboard(request):
    return render(request, 'core/safety_dashboard.html')

@login_required
def deactivate_safety_mode(request):
    if request.method == 'POST':
        # Stop voice monitoring
        try:
            stop_voice_monitoring()
        except Exception as e:
            print(f"Error stopping voice monitoring: {e}")
        
        # Deactivate safety session
        active_session = SafetySession.objects.filter(
            user=request.user,
            is_active=True
        ).first()
        
        if active_session:
            active_session.is_active = False
            active_session.end_time = timezone.now()
            active_session.save()
            
            profile = request.user.userprofile
            profile.is_safety_mode_active = False
            profile.save()
            
            messages.success(request, 'Safety mode deactivated! Voice monitoring stopped.')
    
    return redirect('home')

@login_required
def emergency_alert(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        map_link = data.get('map_link')
        description = data.get('description', 'Voice distress detected')

        # Build location details string robustly
        location_details = ""
        if latitude is not None and longitude is not None:
            location_details = f"Latitude: {latitude}, Longitude: {longitude}"
            if not map_link:
                map_link = f"https://maps.google.com/?q={latitude},{longitude}"
            location_details += f"\nGoogle Maps: {map_link}"
        else:
            location_details = "Location not available"

        active_session = SafetySession.objects.filter(
            user=request.user,
            is_active=True
        ).first()

        if active_session:
            alert = EmergencyAlert.objects.create(
                safety_session=active_session,
                alert_type='voice',
                location=f"{latitude},{longitude}" if latitude and longitude else "",
                description=description,
                shown_to_user=False
            )

            # Send alerts to emergency contacts
            for contact in request.user.userprofile.emergency_contacts.all():
                message = (
                    f"EMERGENCY ALERT from {request.user.get_full_name()}!\n"
                    f"Location: {location_details}\n"
                    f"Description: {description}\n"
                    f"Time: {timezone.now()}\n"
                )
                send_mail(
                    'EMERGENCY ALERT - SirenShield',
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [contact.email],
                    fail_silently=False,
                )

            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

@login_required
def process_voice(request):
    if request.method == 'POST':
        try:
            # Handle both FormData and JSON requests
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Handle FormData (from JavaScript)
                audio_file = request.FILES.get('audio')
                location = request.POST.get('location', '')
                
                if not audio_file:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No audio file received'
                    }, status=400)
                
                # Read audio data
                audio_data = audio_file.read()
                
            else:
                # Handle JSON request (fallback)
                data = json.loads(request.body)
                audio_data = data.get('audio')
                location = data.get('location', '')
                
                if not audio_data:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No audio data received'
                    }, status=400)

            # Use speech recognition to detect emergency phrase
            detector = VoiceSpeechDetector()
            result = detector.detect_emergency_phrase(audio_data)
            
            print(f"Speech recognition result: {result}")
            
            # Check if emergency phrase was detected
            if result['is_emergency']:
                # Parse location if available
                location_data = {}
                if location:
                    try:
                        lat, lng = location.split(',')
                        location_data = {
                            'latitude': float(lat),
                            'longitude': float(lng)
                        }
                    except:
                        pass
                
                # Create emergency alert
                active_session = SafetySession.objects.filter(
                    user=request.user,
                    is_active=True
                ).first()
                
                if active_session:
                    alert = EmergencyAlert.objects.create(
                        safety_session=active_session,
                        alert_type='voice',
                        location=location,
                        description=f"Emergency phrase detected: '{result['text']}'",
                        shown_to_user=False
                    )
                    
                    # Send alerts to emergency contacts
                    for contact in request.user.userprofile.emergency_contacts.all():
                        send_emergency_alert(contact, request.user, location_data)
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Emergency alert sent',
                        'detected_text': result['text'],
                        'is_emergency': True
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Safety mode not active'
                    }, status=400)
            else:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Voice processed - no emergency detected',
                    'detected_text': result['text'],
                    'is_emergency': False
                })

        except Exception as e:
            print('Error in process_voice:', str(e))
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

def send_emergency_alert(contact, user, location):
    """Send emergency alert to a contact"""
    try:
        # Parse location data
        lat = location.get('latitude')
        lng = location.get('longitude')
        
        # Create OpenStreetMap link
        map_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=15/{lat}/{lng}"
        
        subject = f"EMERGENCY ALERT: {user.get_full_name()} needs help!"
        message = f"""
        EMERGENCY ALERT!
        
        {user.get_full_name()} has triggered an emergency alert.
        They may be in danger and need immediate assistance.
        
        Location: {map_link}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Please respond immediately!
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [contact.email],
            fail_silently=False,
        )
        
        # Update alert status
        Alert.objects.filter(user=user, status='active').update(
            status='notified',
            notified_at=datetime.now()
        )
        
    except Exception as e:
        print(f"Error sending alert: {str(e)}")

@login_required
def get_police_stations(request):
    """Get nearby police stations using OpenStreetMap Overpass API"""
    if request.method == 'GET':
        try:
            lat = request.GET.get('lat')
            lon = request.GET.get('lon')
            
            if not lat or not lon:
                return JsonResponse({'error': 'Location coordinates required'}, status=400)
            
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
                        'phone': element.get('tags', {}).get('phone', '')
                    }
                    stations.append(station)
                
                return JsonResponse({'stations': stations})
            
            return JsonResponse({'error': 'Failed to fetch police stations'}, status=500)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def voice_monitoring_status(request):
    """Check if voice monitoring is active"""
    if request.method == 'GET':
        return JsonResponse({
            'is_monitoring': is_monitoring_active(),
            'user_safety_mode': request.user.userprofile.is_safety_mode_active
        })
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def check_emergency_alerts(request):
    """Check for recent emergency alerts"""
    if request.method == 'GET':
        # Get the most recent unshown emergency alert for this user
        recent_alert = EmergencyAlert.objects.filter(
            safety_session__user=request.user,
            alert_type='voice',
            shown_to_user=False,
            timestamp__gte=timezone.now() - timedelta(minutes=5)  # Last 5 minutes
        ).order_by('-timestamp').first()
        
        if recent_alert:
            # Mark the alert as shown to prevent repeated notifications
            recent_alert.shown_to_user = True
            recent_alert.save()
            
            return JsonResponse({
                'has_emergency': True,
                'alert_id': recent_alert.id,
                'description': recent_alert.description,
                'location': recent_alert.location,
                'timestamp': recent_alert.timestamp.isoformat()
            })
        
        return JsonResponse({'has_emergency': False})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
