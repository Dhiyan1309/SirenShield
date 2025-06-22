from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, EmergencyContact

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ('name', 'relationship', 'phone_number', 'email')
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'example@email.com'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1234567890'}),
        }

class SafetyModeForm(forms.Form):
    location = forms.CharField(max_length=255, required=False)
    duration = forms.IntegerField(min_value=1, max_value=24, required=False,
                                help_text='Duration in hours (optional)') 