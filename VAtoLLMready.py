from flask import Flask, request
from faster_whisper import WhisperModel
import subprocess
import wave
import os
import requests
import numpy as np
import sounddevice as sd

app = Flask(__name__)

print("Whisper modeli yükleniyor...")
model = WhisperModel("small", device="cpu", compute_type="int8")
print("Model hazır")


# Türkçe karakter temizleme
def turkish_fix(text):

    replacements = {
        "ç":"c","Ç":"C",
        "ğ":"g","Ğ":"G",
        "ı":"i","İ":"I",
        "ö":"o","Ö":"O",
        "ş":"s","Ş":"S",
        "ü":"u","Ü":"U"
    }

    for k,v in replacements.items():
        text = text.replace(k,v)

    return text


# Ollama çağrısı
def ask_ollama(prompt):

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "mistral",
        "prompt": "Asistan: Kisa cevap ver. En fazla 30 kelime. Sadece Turkce cevap ver. Aciklama yapma.\n\nKullanici: " + prompt + "\nAsistan:",
        "stream": False,
        "options": {
            "num_predict": 80,
            "temperature": 0.2
        }
    }

    response = requests.post(url, json=data)

    result = response.json()

    return result["response"]


@app.route("/audio", methods=["POST"])
def receive_audio():

    print("\n===== YENI SES GELDI =====")

    raw_file = "input.raw"
    wav_file = "input.wav"

    data = request.data

    print("Gelen veri:", len(data))

    # RAW kaydet
    with open(raw_file, "wb") as f:
        f.write(data)

    # WAV oluştur
    with wave.open(wav_file, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(data)

    print("Whisper calisiyor...")

    segments, info = model.transcribe(
        wav_file,
        language="tr"
    )

    text = ""

    for seg in segments:
        text += seg.text.strip() + " "

    print("Algilanan:", text)

    # LLM cevap
    cevap = ask_ollama(text)

    if cevap.strip() == "":
        cevap = "Anlasilmadi"

    cevap = turkish_fix(cevap)
    cevap = cevap.replace('"',"")
    cevap = cevap.replace("\n"," ")

    print("LLM cevabi:", cevap)

    # metni dosyaya yaz
    with open("text.txt", "w", encoding="utf-8") as f:
        f.write(cevap)

    print("Piper calisiyor...")

    subprocess.run(
        "piper --model tr_TR-dfki-medium.onnx --output_file reply.wav < text.txt",
        shell=True
    )

    # wav oku
    with wave.open("reply.wav", "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)
        samplerate = wf.getframerate()

    # PC hoparlöründen çal
    print("PC hoparlorde oynatiliyor...")
    sd.play(audio, samplerate)
    sd.wait()

    # ESP için header at
    with open("reply.wav","rb") as f:
        f.seek(44)
        audio_data = f.read()

    return audio_data


print("SERVER BASLADI")

app.run(host="0.0.0.0", port=5000)