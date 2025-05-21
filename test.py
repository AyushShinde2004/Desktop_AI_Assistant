import speech_recognition as sr
from dotenv import load_dotenv
import os
import winsound
import datetime
import time
import pygame
import io
import re
import requests
import pvporcupine
from gtts import gTTS
import pyaudio
import numpy as np
from pydub import AudioSegment
import threading
import json
from media_controller import handle_media_command
from nlp_processor import NLPProcessor
from volume_control import VolumeController
import torch
from speech_recognition import AudioData
from gemini_handler import GeminiHandler



API_USAGE_FILE = "api_usage.json"


load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

VOICE_KEYS = [
    os.getenv('VOICE_API_KEY_1'),
    os.getenv('VOICE_API_KEY_2'),
    os.getenv('VOICE_API_KEY_3')
]

usage_tracker = {key: 0 for key in VOICE_KEYS}
current_key_index = 0
pygame.mixer.init()
nlp = NLPProcessor()
vc = VolumeController()


recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.7  # Faster pause detection
microphone = sr.Microphone()
with microphone as source:
    recognizer.adjust_for_ambient_noise(source, duration=0.5)

conversation_history = [
    {"role": "user", "parts": [{"text": "You are Grace, a helpful AI assistant. Keep responses very very short."}]}
]
reminders = []
reminder_thread_running = False
api_usage_stats = {"voice_api": 0, "gemini_api": 0}




def play_audio(audio_stream):
    pygame.mixer.music.load(audio_stream, "mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def load_api_usage():
    if os.path.exists(API_USAGE_FILE):
        with open(API_USAGE_FILE, "r") as file:
            data = json.load(file)
            return data.get("api_usage", {"voice_api": 0, "gemini_api": 0}), data.get("current_key_index", 0)
    return {"voice_api": 0, "gemini_api": 0}, 0 

def save_api_usage():
    with open(API_USAGE_FILE, "w") as file:
        json.dump({"api_usage": api_usage_stats, "current_key_index": current_key_index}, file)

api_usage_stats, current_key_index = load_api_usage()

def log_api_usage(api_name, duration=0):
    global api_usage_stats 
    if api_name in api_usage_stats:
        if duration == 0: 
            start_time = time.time()  
            return start_time  
        else:
            api_usage_stats[api_name] += duration
            save_api_usage()
    return None 

def show_api_usage():
    stats_text = "API Usage Stats:\n"
    for api, usage in api_usage_stats.items():
        stats_text += f"{api}: {usage:.2f} seconds\n"
    print(stats_text) 
    with open("api_usage.log", "w") as log_file:
        log_file.write(stats_text)

def switch_api_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(VOICE_KEYS)
    save_api_usage()
    return VOICE_KEYS[current_key_index]

def reset_conversation():
    global conversation_history
    conversation_history = []
    say("history Gone.")

def add_reminder(reminder_text, delay_minutes):
    global reminders
    trigger_time = time.time() + delay_minutes * 60
    reminders.append((reminder_text, trigger_time))
    say(f"Reminder set for {delay_minutes} minutes from now.")

def play_alarm_sound():
    for _ in range(3):
        winsound.Beep(1000, 700) 
        time.sleep(0.3)

def check_reminders():
    global reminders
    reminder_thread_running = True
    while reminder_thread_running:
        current_time = time.time()
        for reminder in reminders[:]:
            reminder_text, trigger_time = reminder
            if current_time >= trigger_time:
                play_alarm_sound()
                say(f"Reminder: {reminder_text}")  
                reminders.remove(reminder)  
        time.sleep(1)

def get_weather():
    try:
        city_name = "Pune" 
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather = data['weather'][0]['description']
            temperature = data['main']['temp']
            return f"The weather in Pune is {weather} with a temperature of {temperature}°C."
        else:
            return f"Error fetching weather: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def say(text, voice_id="ZF6FPAbjXT4488VcRRnw"):
    global usage_tracker, current_key_index
    try:
         #Choose between ElevenLabs and gTTS based on API availability
        #if VOICE_KEYS[current_key_index]:
            # ElevenLabs implementation
        #    current_key = VOICE_KEYS[current_key_index]
        #    headers = {"xi-api-key": current_key, "Content-Type": "application/json"}
        #    payload = {"text": text, "voice_settings": {"stability": 0.5, "clarity": 0.5, "similarity_boost": 0.75}}
        #    API_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        #    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
        #    
        #    if response.status_code == 200:
        #        audio_stream = io.BytesIO(response.content)
        #        audio_thread = threading.Thread(target=play_audio, args=(audio_stream,))
        #        audio_thread.start()
        #else:
            def _gtts_play():
                tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
                audio_stream = io.BytesIO()
                tts.write_to_fp(audio_stream)
                audio_stream.seek(0)
                play_audio(audio_stream)
            
            threading.Thread(target=_gtts_play).start()

    except Exception as e:
        print(f"Error in generating speech: {e}")

def get_gemini_response(data):
    global conversation_history
    try:
        query = data.get("query", "")
        history = data.get("history", [])

        chat_parts = ""
        for turn in history:
            if "user" in turn:
                chat_parts += f"User: {turn['user']}\n"
            if "assistant" in turn:
                chat_parts += f"Assistant: {turn['assistant']}\n"

        prompt = f"""System: You are Grace, a helpful voice assistant. Keep responses very short.
        {chat_parts}User: {query}
            Assistant:"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 200
            }
        }

        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload
        )

        if response.status_code != 200:
            error_msg = f"Error {response.status_code}: {response.text}"
            print(f"Gemini API Error: {error_msg}")
            return error_msg

        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        print(f"Gemini Processing Error: {str(e)}")
        return "Sorry, I'm having trouble answering that right now."



gemini_handler = GeminiHandler(
    gemini_func=get_gemini_response,
    weather_func=get_weather
)

model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad', 
    trust_repo=True
)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = model.to(device)

get_speech_timestamps = utils[0]

def takeCommand():
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    SILENCE_THRESHOLD = 0.18
    MIN_SILENCE_DURATION = 0.5  # 300ms of silence to stop
    MIN_SPEECH_DURATION = 0.1   # Require at least 200ms of speech
    POST_SPEECH_BUFFER_FRAMES = 2
    post_buffer_remaining = POST_SPEECH_BUFFER_FRAMES

    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    audio_buffer = []
    speech_detected = False
    silence_counter = 0
    speech_counter = 0

    print("Listening... (Silero VAD active)", next(model.parameters()).device)

    start_time = time.time()

    try:
        while True:
            # Timeout logic (e.g., stop listening after 30 seconds)
            if time.time() - start_time > 30:
                print("[DEBUG] Timeout reached, stopping listening.")
                break

            raw_data = stream.read(CHUNK, exception_on_overflow=False)
            audio_int16 = np.frombuffer(raw_data, np.int16)
            audio_float32 = audio_int16.astype(np.float32) / 32768.0

            speech_prob = model(torch.from_numpy(audio_float32).to(device), RATE).item()

            if speech_prob > SILENCE_THRESHOLD:
                speech_detected = True
                silence_counter = 0
                speech_counter += 1
                audio_buffer.append(raw_data)
            elif speech_detected:
                # Capture a few extra chunks after speech detection
                if post_buffer_remaining > 0:
                    audio_buffer.append(raw_data)
                    post_buffer_remaining -= 1
                    continue

                silence_counter += 1
                if silence_counter > (MIN_SILENCE_DURATION * RATE / CHUNK):
                    # Verify we met minimum speech duration
                    if speech_counter * (CHUNK/RATE) >= MIN_SPEECH_DURATION:
                        break
                    else:
                        # Reset if we didn't get enough speech
                        audio_buffer = []
                        speech_detected = False
                        silence_counter = 0
                        speech_counter = 0

        if len(audio_buffer) < int(0.4 * RATE / CHUNK):
            padding = int(0.4 * RATE / CHUNK) - len(audio_buffer)
            audio_buffer += [b'\x00'*CHUNK]*padding

        audio_bytes = b''.join(audio_buffer)

        audio_segment = AudioSegment(
            data=audio_bytes,
            sample_width=p.get_sample_size(FORMAT),
            frame_rate=RATE,
            channels=CHANNELS
        )
        audio_segment = audio_segment.apply_gain(15)

        audio_data = AudioData(
            frame_data=audio_segment.raw_data,
            sample_rate=RATE,
            sample_width=p.get_sample_size(FORMAT)
        )

        # Recognition attempt
        for attempt in range(2):
            try:
                transcript = recognizer.recognize_google(
                    audio_data,
                    language="en-in",
                    show_all=(attempt == 1)
                )
                if isinstance(transcript, dict):
                    transcript = transcript['alternative'][0]['transcript']
                return transcript.strip().lower()
            except sr.UnknownValueError:
                if attempt == 0:
                    audio_buffer += [b'\x00'*CHUNK]*2
                    audio_bytes = b''.join(audio_buffer)
                    audio_data = AudioData(
                        frame_data=audio_bytes,
                        sample_rate=RATE,
                        sample_width=p.get_sample_size(FORMAT)
                    )
                else:
                    return None

        return None

    except Exception as e:
        print(f"[ERROR] Error in takeCommand: {e}")
        return None

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def wakeUp():
    porcupine = pvporcupine.create(
        access_key=os.getenv('PORC_API_KEY'),
        keyword_paths=[r"C:\Users\LEGION\OneDrive\Desktop\Python Shit\A.I Assistant\selena_en_windows_v3_0_0.ppn"]
    )
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=512
    )
    print("Listening for wake word...")
    while True:
        try:
            audio_data = stream.read(512)
            audio_data = np.frombuffer(audio_data, dtype=np.int16)
            result = porcupine.process(audio_data)
            if result >= 0:
                return True
            time.sleep(0.01) 
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == '__main__':
    reminder_thread = threading.Thread(target=check_reminders, daemon=True)
    reminder_thread.start()

    while True:
        if wakeUp():
            #say("uh huh...")  # Non-blocking response   
            transcript = takeCommand()
            print(f"\nRAW INPUT: {transcript}")
            if not transcript:
                say("What")
                continue  

            # Process command
            try:
                command = nlp.parse_command(transcript)
                if command:
                    details = nlp.extract_details(command)
                    # Media commands
                    if command["action"] in ("play_music", "play_playlist", "control_playback"):
                        if handle_media_command(command["action"], details):
                            continue

                    # Volume control
                    elif command["action"] == "set_volume" and "level" in details:
                        vc.set_volume(details["level"])
                        say("Done")
                        continue

                    # AI queries
                    elif command["intent"] == "ai_query":
                        response = gemini_handler.process_input(transcript)
                        nlp.context["last_intent"] = "ai_query"  # Track context
                        say(response)
                        continue

                    elif command["intent"] == "ai_followup":
                        # Use full conversation context
                        context = " ".join(nlp.context["conversation"][-2:])
                        response = gemini_handler.process_input(context)
                        say(response)
                        continue

                # Special cases
                elif "remind me" in transcript.lower():
                    match = re.search(r'remind me in (\d+)\s*(?:minutes?|mins?|m)?(?: about (.+))?', transcript.lower())
                    if match:
                        delay_minutes = int(match.group(1))
                        reminder_text = match.group(2) or "your reminder"
                        add_reminder(reminder_text, delay_minutes)
                    else:
                        say("Please specify a valid time.")
                    continue

                elif "the time" in transcript.lower():
                    now = datetime.datetime.now()
                    say(f"The time is {now.hour} and {now.minute} minutes")
                    continue

                elif "open youtube music" in transcript.lower():
                    os.system(r'"C:\Users\LEGION\AppData\Local\Google\Chrome\Application\chrome_proxy.exe" --profile-directory=Default --app-id=cinhimbnkkaeohfgghhklpknlkffjgod')
                    continue

                elif "weather" in transcript.lower():
                    say(get_weather())
                    continue

                elif "api time" in transcript.lower():
                    show_api_usage()
                    continue

                elif "quit yourself" in transcript.lower():
                    say("Hope to see you again.")
                    exit()

                elif "reset chat" in transcript.lower():
                    reset_conversation()
                    continue

                elif "nothing" in transcript.lower():
                    say("ok")
                    continue  # Silent return to wake word detection

            except Exception as e:
                print(f"Error processing command: {e}")
                say("Something went wrong")        