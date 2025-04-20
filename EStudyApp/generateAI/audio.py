# utils/audio.py
import os
import requests
import tempfile
from pydub import AudioSegment
import speech_recognition as sr

# Thiết lập đường dẫn ffmpeg phù hợp hệ điều hành
if os.name == 'nt':
    ffmpeg_path = r"D:\tools-upgraders\ffmpeg-2025-04-14-git-3b2a9410ef-essentials_build\bin"
    os.environ["PATH"] += os.pathsep + ffmpeg_path
    AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")
    AudioSegment.ffprobe = os.path.join(ffmpeg_path, "ffprobe.exe")
else:
    AudioSegment.converter = "/usr/bin/ffmpeg"
    AudioSegment.ffprobe = "/usr/bin/ffprobe"

# In kiểm tra
print("✅ FFMPEG PATH:", AudioSegment.converter)
print("✅ FFPROBE PATH:", AudioSegment.ffprobe)


def transcribe_audio_from_urls(audio_urls):
    """
    Nhận danh sách URL audio, trích xuất văn bản bằng Google Speech Recognition.
    """
    if not isinstance(audio_urls, list):
        audio_urls = [audio_urls]

    recognizer = sr.Recognizer()
    transcripts = []

    for url in audio_urls:
        try:
            # Tải về file mp3 tạm thời
            response = requests.get(url)
            print(response)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                temp_mp3.write(response.content)
                mp3_path = temp_mp3.name

            print(f"🎧 Đã tải về mp3: {mp3_path}")

            # Chuyển sang wav
            wav_path = mp3_path.replace(".mp3", ".wav")
            audio = AudioSegment.from_mp3(mp3_path)
            audio.export(wav_path, format="wav")

            print(f"🔄 Đã chuyển sang wav: {wav_path}")

            # Dùng speech_recognition nhận dạng
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data, language='en-US')
                    print(f"🗣️  Nhận dạng: {text}")
                    transcripts.append(text.strip())
                except sr.UnknownValueError:
                    transcripts.append("⚠️ Không thể nhận dạng nội dung âm thanh.")
                except sr.RequestError as e:
                    transcripts.append(f"❌ Lỗi kết nối tới Google API: {e}")

            os.remove(mp3_path)
            os.remove(wav_path)

        except Exception as e:
            transcripts.append(f"❌ Không xử lý được audio từ {url}: {str(e)}")

    return "\n".join(transcripts)
