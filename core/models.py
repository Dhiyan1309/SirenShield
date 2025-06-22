from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contacts = models.ManyToManyField('EmergencyContact', related_name='user_profiles', blank=True)
    is_safety_mode_active = models.BooleanField(default=False)
    last_safety_mode_activation = models.DateTimeField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    role = models.CharField(max_length=50, default='Guardian')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"

class EmergencyContact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('Family', 'Family'),
        ('Friend', 'Friend'),
        ('Neighbor', 'Neighbor'),
        ('Other', 'Other')
    ]
    
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.relationship}"

class SafetySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"Safety Session for {self.user.email} - {self.start_time}"

class EmergencyAlert(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ]
    
    safety_session = models.ForeignKey(SafetySession, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    alert_type = models.CharField(max_length=50)  # voice, manual, etc.
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    shown_to_user = models.BooleanField(default=False)  # Track if alert has been shown to user
    
    def __str__(self):
        return f"Emergency Alert for {self.safety_session.user.email} - {self.timestamp}"

class Alert(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('notified', 'Notified'),
        ('resolved', 'Resolved')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50)  # voice, manual, etc.
    location = models.TextField()  # JSON string of location data
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Alert for {self.user.email} - {self.created_at}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
