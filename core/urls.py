from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile, name='update_profile'),
    path('profile/add-contact/', views.add_emergency_contact, name='add_emergency_contact'),
    path('profile/edit-contact/', views.edit_emergency_contact, name='edit_emergency_contact'),
    path('profile/delete-contact/<int:contact_id>/', views.delete_emergency_contact, name='delete_emergency_contact'),
    path('profile/get-contact/<int:contact_id>/', views.get_contact_details, name='get_contact_details'),
    path('safety-mode/', views.safety_mode, name='safety_mode'),
    path('safety-dashboard/', views.safety_dashboard, name='safety_dashboard'),
    path('deactivate-safety/', views.deactivate_safety_mode, name='deactivate_safety_mode'),
    path('emergency-alert/', views.emergency_alert, name='emergency_alert'),
    path('police-stations/', views.get_police_stations, name='get_police_stations'),
    path('process-voice/', views.process_voice, name='process_voice'),
    path('voice-monitoring-status/', views.voice_monitoring_status, name='voice_monitoring_status'),
    path('check-emergency-alerts/', views.check_emergency_alerts, name='check_emergency_alerts'),
    path('guardian-profile/', views.guardian_profile, name='guardian_profile'),
    path('update-notification-preferences/', views.update_notification_preferences, name='update_notification_preferences'),
] 