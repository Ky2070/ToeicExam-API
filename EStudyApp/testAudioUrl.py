import os
import requests
from pydub import AudioSegment
import speech_recognition as sr

# Trường hợp trên local, cập nhật đường dẫn cho FFmpeg và FFprobe
if os.name == 'nt':  # Nếu là hệ điều hành Windows
    os.environ["PATH"] += os.pathsep + r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin"
    AudioSegment.converter = r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin\ffmpeg.exe"
    AudioSegment.ffprobe = r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin\ffprobe.exe"
else:  # Nếu là môi trường deploy (Linux hoặc khác)
    AudioSegment.converter = "/usr/bin/ffmpeg"  # Cập nhật đường dẫn FFmpeg cho server
    AudioSegment.ffprobe = "/usr/bin/ffprobe"  # Cập nhật đường dẫn FFprobe cho server

# Kiểm tra FFmpeg và FFprobe
print("✅ Kiểm tra FFmpeg:", os.path.isfile(AudioSegment.converter))
print("✅ Kiểm tra FFprobe:", os.path.isfile(AudioSegment.ffprobe))

# Tải file mp3 từ URL
url = 'https://s4-media1.study4.com/media/economy1000/test10_audios/q32-34.mp3'
response = requests.get(url)
with open("audio.mp3", "wb") as f:
    f.write(response.content)

# Chuyển mp3 sang wav
audio = AudioSegment.from_mp3("audio.mp3")
audio.export("audio.wav", format="wav")

# Nhận dạng giọng nói
r = sr.Recognizer()
with sr.AudioFile("audio.wav") as source:
    audio_data = r.record(source)
    try:
        text = r.recognize_google(audio_data)
        print("🎧 Nội dung trích xuất từ audio:")
        print(text)
    except sr.UnknownValueError:
        print("⚠️ Không nhận diện được nội dung.")
    except sr.RequestError as e:
        print(f"❌ Lỗi kết nối đến Google API: {e}")
