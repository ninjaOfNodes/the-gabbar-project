import pyttsx3
import speech_recognition as sr
import requests
import threading

engine = pyttsx3.init()
engine.setProperty('rate', 175)
OLLAMA_URL = "http://localhost:11434/api/generate"

def speak(text):
    print(f"Gabbar: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("🧠 Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"You: {query}")
        return query.lower()
    except:
        return ""

def query_ollama(prompt):
    try:
        payload = {
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json()["response"]
    except Exception as e:
        return f"Error: {e}"

def gabbar_loop():
    speak("Gabbar is online.")
    while True:
        text = listen()
        if "gabbar" in text:
            speak("Yes, how can I help?")
            command = text.replace("gabbar", "").strip()
            if command == "":
                speak("Please say your request.")
                command = listen()

            if any(word in command for word in ["exit", "stop", "quit"]):
                speak("Shutting down.")
                break

            reply = query_ollama(command)
            speak(reply)
        else:
            print("🕑 Waiting for 'Gabbar'...")
