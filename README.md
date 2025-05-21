# 🤖 AI Voice Assistant
-AI Voice Assistant is an advanced voice-controlled application that seamlessly integrates speech recognition, AI-powered responses, web automation, and media playback. Designed for efficiency and ease of use, it transforms voice commands into powerful actions.
## 🚀 Overview
This AI-powered voice assistant integrates multiple services, including speech recognition, text-to-speech, web automation, and Spotify playback. It can:
- Recognize voice commands 🎙️
- Play YouTube videos 📺
- Control system volume 🔊
- Set reminders ⏰
- Provide weather updates ☁️
- Control Spotify playback 🎵

## 🛠️ Technologies Used
- **Speech Recognition** (`speech_recognition`)
- **Text-to-Speech** (`pvleopard`, `elevenlabs API`)
- **Web Automation** (`selenium`, `undetected_chromedriver`)
- **Media Playback** (`pygame`, `pydub`)
- **Music Streaming** (`spotipy`)
- **Environment Variables** (`dotenv`)

## 🔧 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/AyushShinde2004/Ai_assistant.git
   cd Ai_assistant
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file:
   ```plaintext
    GEMINI_API_KEY=
    PORC_API_KEY=
    VOICE_API_KEY_1=
    VOICE_API_KEY_2=
    VOICE_API_KEY_3=
    SPOTIFY_CLIENT_ID=
    SPOTIFY_CLIENT_SECRET=
    SPOTIFY_REDIRECT_URI=
    WEATHER_API_KEY=
   ```

## 🎙️ Usage
Run the assistant:
```bash
python Assistant.py
```

### Example Commands:
- **"Play Imagine Dragons on Spotify"** 🎶
- **"Play TheWeeknd on Youtube"** 🎶
- **"Set a reminder in 10 minutes"** ⏳
- **"What's the weather like?"** 🌦️
- **"Turn volume to 50%"** 🔈

## 📝 Features
### 🗣️ Speech Recognition & AI Responses
- Uses Google Speech Recognition to process voice commands.
- Interacts with the Gemini API for AI-generated responses.

### 🎶 Music & Video Control
- Plays music on **Spotify**.
- Plays videos on **YouTube** using Selenium automation.
- Controls **system volume**.

### ⏰ Reminder System
- Set and check reminders with automatic voice alerts.

### ☁️ Weather Updates
- Retrieves real-time weather information via the **OpenWeather API**.

## 🤝 Contribution
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Commit changes:
   ```bash
   git commit -m "Added new feature"
   ```
4. Push and create a pull request.

## 📜 License
This project is licensed under the MIT License.

---
🚀 Built with Python and Passion! ❤️
