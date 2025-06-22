import speech_recognition as sr
import tempfile
import os
from django.conf import settings

class VoiceSpeechDetector:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.emergency_phrase = "help me"
    
    def detect_emergency_phrase(self, audio_data):
        """Detect if the audio contains the emergency phrase 'help me'"""
        try:
            # Create a temporary file to save the audio data
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Use speech recognition to convert audio to text
            with sr.AudioFile(temp_file_path) as source:
                audio = self.recognizer.record(source)
                
                # Try to recognize speech
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Recognized text: {text}")
                    
                    # Check if the emergency phrase is in the recognized text
                    is_emergency = self.emergency_phrase in text
                    
                    return {
                        'text': text,
                        'is_emergency': is_emergency,
                        'confidence': 1.0 if is_emergency else 0.0
                    }
                    
                except sr.UnknownValueError:
                    print("Speech recognition could not understand audio")
                    return {
                        'text': '',
                        'is_emergency': False,
                        'confidence': 0.0
                    }
                except sr.RequestError as e:
                    print(f"Could not request results from speech recognition service; {e}")
                    return {
                        'text': '',
                        'is_emergency': False,
                        'confidence': 0.0
                    }
                    
        except Exception as e:
            print(f"Error processing audio: {e}")
            return {
                'text': '',
                'is_emergency': False,
                'confidence': 0.0
            }
        finally:
            # Clean up temporary file
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

# For backward compatibility
class VoiceEmotionDetector(VoiceSpeechDetector):
    def __init__(self):
        super().__init__()
    
    def predict(self, audio_data):
        """Predict if audio contains emergency phrase (for backward compatibility)"""
        result = self.detect_emergency_phrase(audio_data)
        return 'distress' if result['is_emergency'] else 'neutral'

def train_model():
    """Train the emotion detection model"""
    # This function would be used to train the model on a dataset of emotional speech
    # For now, we'll use a pre-trained model
    pass 