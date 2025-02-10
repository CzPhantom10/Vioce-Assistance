import streamlit as st
import pyttsx3
import speech_recognition as sr
import requests
import json

# Initialize TTS engine
engine = pyttsx3.init()

# Spotify API credentials (replace with your own)
SPOTIFY_CLIENT_ID = 'your_client_id'
SPOTIFY_CLIENT_SECRET = 'your_client_secret'
SPOTIFY_ACCESS_TOKEN = None

def get_spotify_access_token():
    global SPOTIFY_ACCESS_TOKEN
    if SPOTIFY_ACCESS_TOKEN is None:
        url = "https://accounts.spotify.com/api/token"
        payload = "grant_type=client_credentials"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'
        }
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            SPOTIFY_ACCESS_TOKEN = response.json()['access_token']
        else:
            st.error("Failed to get Spotify access token.")
            return None
    return SPOTIFY_ACCESS_TOKEN

def play_song_on_spotify(song_name):
    token = get_spotify_access_token()
    if token:
        search_url = f"https://api.spotify.com/v1/search?q={song_name}&type=track"
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            tracks = response.json()['tracks']['items']
            if tracks:
                track_uri = tracks[0]['uri']
                play_url = "https://api.spotify.com/v1/me/player/play"
                play_payload = json.dumps({"uris": [track_uri]})
                play_response = requests.put(play_url, headers=headers, data=play_payload)
                if play_response.status_code == 204:
                    return f"Playing '{tracks[0]['name']}' on Spotify."
                else:
                    return "Failed to play the song on Spotify."
            else:
                return "No tracks found."
        else:
            return "Error searching for the song."
    return "Spotify access token is not available."

def embed_youtube_video(video_id):
    return f"""
    <iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" 
    frameborder="0" allowfullscreen></iframe>
    """

def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except Exception as e:
        st.error("Error transcribing audio: " + str(e))
        return None

def generate_response(prompt):
    # Placeholder for GPT-3.5 response generation
    response = "This is a placeholder response."  # Replace with actual API call
    return response

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def main():
    st.sidebar.title("Voice Assistant")
    st.sidebar.markdown("""
        ### Instructions:
        1. Click the **Record** button.
        2. Say 'OK Google' to activate the recording.
        3. Ask your question or request a song/video.
        4. Listen to the response from the assistant.
    """)
    
    st.sidebar.markdown("""
        ### Features:
        - Provide you with any information.
        - Play songs on Spotify.
        - Play videos on YouTube.
        - More features are still to be discovered.
    """)

    if st.sidebar.button("Start Recording"):
        st.write("Say 'OK Google' to start recording your question...")
        
        # Set up the recognizer
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio)
                st.write(f"You said: {transcription}")
                
                if transcription.lower() == "ok google":
                    st.write("Recording your question...")
                    filename = "input.wav"
                    with sr.Microphone() as source:
                        audio = recognizer.listen(source)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())
                    
                    text = transcribe_audio_to_text(filename)
                    if text:
                        st.write(f"You asked: {text}")
                        
                        # Check for YouTube and Spotify commands
                        if "play" in text.lower() and "on spotify" in text.lower():
                            song_name = text.lower().replace("play", "").replace("on spotify", ""). strip()
                            response = play_song_on_spotify(song_name)
                            st.write(response)
                            speak_text(response)
                        elif "open" in text.lower() and "youtube" in text.lower():
                            video_id = "dQw4w9WgXcQ"  # Example video ID, you can modify this based on user input
                            st.markdown(embed_youtube_video(video_id), unsafe_allow_html=True)
                            speak_text("Opening YouTube video.")
                        else:
                            response = generate_response(text)
                            st.write(f"GPT-3.5-turbo says: {response}")
                            speak_text(response)
            except Exception as e:
                st.error("An error occurred: " + str(e))

if __name__ == "__main__":
    main()