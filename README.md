# SirenShield - Women's Safety App

SirenShield is a comprehensive women's safety application built with Django that provides real-time voice monitoring, emergency alerts, and location tracking to ensure user safety.

## 🚨 Features

### Core Safety Features
- **Voice Monitoring**: Real-time voice detection using speech recognition to identify emergency phrases like "help me"
- **Emergency Alerts**: Automatic notification system that sends alerts to emergency contacts with location details
- **Location Tracking**: GPS-based location tracking with fallback to IP geolocation
- **Police Station Finder**: Automatic detection of nearby police stations with navigation links
- **Safety Mode**: Active monitoring mode with continuous voice surveillance

### User Management
- **User Registration & Authentication**: Secure user accounts with email-based authentication
- **Emergency Contacts**: Manage trusted contacts who receive emergency notifications
- **Profile Management**: User profiles with customizable notification preferences
- **Guardian System**: Support for guardian accounts to monitor multiple users

### Technical Features
- **Real-time Voice Processing**: Server-side voice monitoring using Python speech recognition
- **Email Notifications**: Automated emergency emails with detailed location information
- **Interactive Maps**: Integration with OpenStreetMap for police station locations
- **Responsive UI**: Modern, mobile-friendly interface built with Bootstrap

## 🛠️ Technology Stack

- **Backend**: Django 5.2, Python 3.13
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Voice Recognition**: SpeechRecognition library
- **Maps**: OpenStreetMap API, Leaflet.js
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Django Allauth

## 📋 Prerequisites

Before running this application, make sure you have:

- Python 3.8 or higher
- pip (Python package installer)
- Git
- A microphone for voice testing
- Email service for notifications (Gmail recommended)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/sirenshield.git
cd sirenshield
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 📱 Usage

### 1. User Registration
- Visit the registration page and create an account
- Verify your email address
- Complete your profile setup

### 2. Add Emergency Contacts
- Navigate to your profile
- Add trusted contacts (family, friends, neighbors)
- Ensure they have valid email addresses

### 3. Activate Safety Mode
- Go to the Safety Mode page
- Click "Activate Safety Mode"
- The system will start voice monitoring

### 4. Emergency Detection
- When you say "help me" clearly, the system will:
  - Detect the emergency phrase
  - Send email alerts to your emergency contacts
  - Open navigation to the nearest police station
  - Display emergency notifications

### 5. Deactivate Safety Mode
- Use the "Deactivate Safety Mode" button to stop monitoring

## 🔧 Configuration

### Email Settings
To enable email notifications, configure your email settings in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Voice Recognition Settings
The voice monitoring sensitivity can be adjusted in `core/voice_monitor.py`:

```python
# Adjust timeout and phrase detection settings
timeout = 5  # seconds to wait for phrase
phrase_timeout = 3  # seconds to wait for phrase completion
```

## 🧪 Testing

### Voice Monitoring Test
```bash
python manage.py test_location
python manage.py test_voice_monitor
```

### Manual Testing
1. Activate safety mode
2. Say "help me" clearly into your microphone
3. Check that emergency alerts are sent
4. Verify email notifications are received

## 📁 Project Structure

```
SirenShield_pro/
├── core/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── voice_monitor.py    # Voice monitoring logic
│   ├── voice_detection.py  # Speech recognition
│   └── management/         # Custom management commands
├── sireshield/             # Django project settings
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploaded files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔒 Security Features

- **Authentication**: Secure user authentication with Django Allauth
- **CSRF Protection**: Built-in CSRF protection for all forms
- **Input Validation**: Comprehensive input validation and sanitization
- **Secure Headers**: Security headers configured for production
- **Environment Variables**: Sensitive data stored in environment variables

## 🚀 Deployment

### Production Setup
1. Set `DEBUG = False` in settings
2. Configure a production database (PostgreSQL recommended)
3. Set up a production web server (Nginx + Gunicorn)
4. Configure static file serving
5. Set up SSL certificates
6. Configure email service for production

### Docker Deployment (Optional)
```bash
# Build and run with Docker
docker build -t sirenshield .
docker run -p 8000:8000 sirenshield
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/sirenshield/issues) page
2. Create a new issue with detailed information
3. Contact the development team

## 🙏 Acknowledgments

- Django community for the excellent framework
- SpeechRecognition library for voice processing
- OpenStreetMap for mapping services
- Bootstrap for the responsive UI components

## 📊 Version History

- **v1.0.0** - Initial release with core safety features
- **v1.1.0** - Added voice monitoring and emergency alerts
- **v1.2.0** - Enhanced location tracking and police station finder
- **v1.3.0** - Improved UI and notification system

---

**⚠️ Important Note**: This application is designed for educational and personal safety purposes. In real emergency situations, always contact local emergency services (911, 112, etc.) immediately. 