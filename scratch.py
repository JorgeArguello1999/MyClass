from pydub import AudioSegment
import speech_recognition as sr
import os
import sys

# find the webm file
base_dir = "app/static/uploads/audio/"
files = [f for f in os.listdir(base_dir) if f.endswith('.webm')]
if not files:
    print("No webm files found")
    sys.exit(1)

file_path = os.path.join(base_dir, files[-1])
print(f"Testing with file: {file_path}")

try:
    wav_path = file_path.replace('.webm', '.wav')
    print("Exporting to wav...")
    audio = AudioSegment.from_file(file_path, format="webm")
    audio.export(wav_path, format="wav")
    print("Exported to", wav_path)
    
    print("Recognizing...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
    
    print("Contacting Google...")
    text = recognizer.recognize_google(audio_data, language="ko-KR")
    print("Success:", text)
except Exception as e:
    import traceback
    traceback.print_exc()

