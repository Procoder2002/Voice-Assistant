import pyttsx3
import speech_recognition as sr
import spacy
from youtubesearchpython import VideosSearch
import webbrowser
from googleapiclient.discovery import build

# Initialize TTS engine
engine = pyttsx3.init()

# Initialize spaCy language model
nlp = spacy.load("en_core_web_sm")

# Google Custom Search API credentials
API_KEY = "AIzaSyCSZ643CcsxcR_bjoq9Hf7JLyxjOW__2Bg" 
CSE_ID = "75308df5728fc4876"  

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to query Google Custom Search API
def query_google(query):
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        res = service.cse().list(q=query, cx=CSE_ID).execute()
        if 'items' in res:
            return res['items'][0]['snippet']  # Return a short snippet from the first result
        else:
            return "Sorry, I couldn't find any relevant information."
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I couldn't process your request right now."

# Function to classify intent (using spaCy)
def classify_intent(command):
    doc = nlp(command)
    
    # Check if the intent is to "play" a song
    if "play" in command.lower():
        song_name = command.lower().replace("play", "").strip()
        return ("play_music", song_name)
    
    # Check if the intent is to "open" a website
    if "open" in command.lower():
        for token in doc:
            if token.text.lower() in ["google", "youtube", "facebook", "linkedin"]:
                return ("open_website", token.text.lower())

    # Check if the intent is to "ask" a question
    if "what" in command.lower() or "how" in command.lower() or "why" in command.lower():
        return ("ask_question", command)

    return ("unknown", None)

# Function to search and play music on YouTube
def search_and_play_song(song_name):
    try:
        search = VideosSearch(song_name, 1)
        result = search.result()
        video_url = f"https://www.youtube.com/watch?v={result['result'][0]['id']}"
        print(f"Playing: {result['result'][0]['title']} - {video_url}")
        webbrowser.open(video_url)
        speak(f"Playing {result['result'][0]['title']}")
    except Exception as e:
        print(f"Error occurred: {e}")
        speak("Sorry, I couldn't find the song.")

# Main loop to listen for commands
def listen_for_commands():
    while True:
        print("Listening for wake word...")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            try:
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                
                if "jarvis" in command.lower():
                    speak("Yes, how can I assist you?")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio)
                    print(f"Command: {command}")

                    intent, data = classify_intent(command)
                    if intent == "play_music":
                        speak(f"Searching and playing {data}")
                        search_and_play_song(data)
                    elif intent == "open_website":
                        speak(f"Opening {data}")
                        webbrowser.open(f"https://{data}.com")
                    elif intent == "ask_question":
                        response = query_google(data)
                        speak(f"The answer is: {response}")
                    else:
                        speak("I didn't understand that command.")
            except sr.UnknownValueError:
                print("Could not understand the audio.")
            except sr.RequestError as e:
                print(f"Error with speech recognition request; {e}")

if __name__ == "__main__":
    speak("Initializing Jarvis...")
    listen_for_commands()
