import os
import requests
from pydub import AudioSegment
import speech_recognition as sr

# Check if running in Docker
IN_DOCKER = os.environ.get('IN_DOCKER', False)

# Set FFmpeg paths based on environment
if os.name == 'nt':  # Windows
    os.environ["PATH"] += os.pathsep + r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin"
    AudioSegment.converter = r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin\ffmpeg.exe"
    AudioSegment.ffprobe = r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin\ffprobe.exe"
else:  # Linux/Docker
    AudioSegment.converter = "/usr/bin/ffmpeg"
    AudioSegment.ffprobe = "/usr/bin/ffprobe"

# Check FFmpeg installation
print("✅ Checking FFmpeg:", os.path.isfile(AudioSegment.converter))
print("✅ Checking FFprobe:", os.path.isfile(AudioSegment.ffprobe))

# Create directories if they don't exist
os.makedirs("audio", exist_ok=True)
os.makedirs("wav", exist_ok=True)

# Download mp3 file from URL
url = 'https://s4-media1.study4.com/media/economy1000/test10_audios/q32-34.mp3'
response = requests.get(url)
with open("audio/audio.mp3", "wb") as f:
    f.write(response.content)

# Convert mp3 to wav
audio = AudioSegment.from_mp3("audio/audio.mp3")
audio.export("wav/audio.wav", format="wav")

# Speech recognition
r = sr.Recognizer()
with sr.AudioFile("wav/audio.wav") as source:
    audio_data = r.record(source)
    try:
        text = r.recognize_google(audio_data)
        print("🎧 Extracted audio content:")
        print(text)
    except sr.UnknownValueError:
        print("⚠️ Could not recognize content.")
    except sr.RequestError as e:
        print(f"❌ Error connecting to Google API: {e}")
