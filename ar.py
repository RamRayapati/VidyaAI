import streamlit as st
import google.generativeai as genai
from audio_recorder_streamlit import audio_recorder
import numpy as np
import io
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
import re
import base64

# Page settings
st.set_page_config(page_title="🧠🎙 AI Mental Health Support Voice Assistant", layout="wide")

# Configure Gemini API
genai.configure(api_key="AIzaSyCA0gtQoTztkO7wkAyN5q8UpESfCGzLM48")

# Gemini model settings
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    generation_config=generation_config,
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ],
    system_instruction="""
    You are a compassionate and empathetic AI trained to provide mental health support.
    - Always respond in a calm and soothing manner.
    - Use positive reinforcement and validate emotions.
    - Avoid medical diagnoses but encourage seeking professional help.
    - Offer mindfulness tips, breathing exercises, and self-care suggestions.
    Note: Be concise in your responses; don’t give overwhelming replies unnecessarily. Be detailed wherever required.
    """
)

# Clean markdown from Gemini response
def clean_markdown(text):
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'^\s*[-]\s', '', text, flags=re.MULTILINE)
    text = re.sub(r'{1,3}.*?{1,3}', '', text, flags=re.DOTALL)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()

# Audio playback utility
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
        <audio autoplay controls>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)

# Chat session memory
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🧠🎙 AI Mental Health Support Voice Assistant")

st.write("### Tap the mic and speak")
audio = audio_recorder()

if audio is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio)
        tmp_filename = tmp_file.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_filename) as source:
        audio_data = recognizer.record(source)
        try:
            user_input = recognizer.recognize_google(audio_data)
            st.session_state.messages.append({"role": "user", "content": user_input})
        except sr.UnknownValueError:
            st.warning("⚠️ Could not understand audio. Please try again.")
        except sr.RequestError:
            st.error("❌ Speech recognition service is unavailable.")

    os.remove(tmp_filename)

# Show all messages so far
if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get response from Gemini
    conversation_history = [msg["content"] for msg in st.session_state.messages]
    response = model.generate_content(conversation_history)
    response_text = clean_markdown(response.text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})

    with st.chat_message("assistant"):
        st.markdown(response_text)

    # Convert response to female voice using gTTS
    tts = gTTS(text=response_text, lang='en', tld='com.au')  # Australian accent sounds more female

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
        tts.save(audio_file.name)
        audio_path = audio_file.name

    autoplay_audio(audio_path)
