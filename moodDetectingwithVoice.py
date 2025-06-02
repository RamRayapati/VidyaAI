import speech_recognition as sr
from transformers import pipeline

# Load the emotion classifier
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=False
)

# Initialize recognizer
recognizer = sr.Recognizer()

def get_voice_input():
    with sr.Microphone() as source:
        print("🎙️ Listening... (You can say 'stop' to end listening)")
        
        # Adjust for ambient noise levels
        recognizer.adjust_for_ambient_noise(source)
        print("🔊 Adjusting for ambient noise. Please wait...")
        
        try:
            # Increased timeout to 10 seconds and phrase_time_limit to 20 seconds
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
            text = recognizer.recognize_google(audio)
            print(f"🗣️ You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand the audio. Please try again.")
            return None
        except sr.RequestError:
            print("⚠️ Network error. Could not request results.")
            return None
        except sr.WaitTimeoutError:
            print("⏳ Listening timed out. No speech detected.")
            return None

# Start listening
user_input = get_voice_input()

if user_input:
    if "stop" in user_input.lower():
        print("🔴 Listening stopped.")
    else:
        # Run emotion detection
        emotion = emotion_classifier(user_input)
        print(f"💡 Detected emotion: {emotion[0]['label']} with confidence {emotion[0]['score']:.2f}")
