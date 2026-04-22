from flask import Flask, request, send_file
from faster_whisper import WhisperModel
import subprocess
import wave
import os
import requests
import numpy as np
import soundfile as sf

app = Flask(__name__)

print("Whisper modeli yükleniyor...")
model = WhisperModel("small", device="cpu", compute_type="int8")
print("Model hazır")

counter = 0


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


# Ollama LLM çağrısı
def ask_ollama(prompt):

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "phi3:latest",
        "prompt": "Sen kisa cevap veren bir asistansin. Maksimum 1 cumle cevap ver.\n\nKullanici: " + prompt,
        "stream": False,
        "options": {
            "num_predict": 40
        }
    }

    response = requests.post(url, json=data)

    result = response.json()

    return result["response"]


@app.route("/audio", methods=["POST"])
def receive_audio():

    global counter
    counter += 1

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

    print("WAV olusturuldu")

    print("Whisper calisiyor...")

    segments, info = model.transcribe(
        wav_file,
        language="tr",
        beam_size=5,
        condition_on_previous_text=False
    )

    text = ""

    for seg in segments:
        text += seg.text.strip() + " "

    print("Algilanan:", text)

    # LLM cevabı
    cevap = ask_ollama(text)

    if cevap.strip() == "":
        cevap = "Anlasilmadi"

    cevap = turkish_fix(cevap)
    cevap = cevap.replace('"',"")
    cevap = cevap.replace("\n"," ")

    print("LLM cevabi:", cevap)

    print("Piper calisiyor...")
    
    process = subprocess.Popen(
        [
        "piper",
        "--model", "tr_TR-dfki-medium.onnx",
        "--output_file", "reply.wav",
        "--speaker", "0",
        "--length_scale", "1.0",
        "--sample_rate", "16000"
        ],
        stdin=subprocess.PIPE,
        text=True
    )

    
    process.communicate(cevap)
    # wav sample rate düzelt
    data_audio, sr = sf.read("reply.wav")

    import scipy.signal
    data_audio = scipy.signal.resample_poly(data_audio, 16000, sr)

    sf.write("reply.wav", data_audio, 16000)

    if os.path.exists("reply.wav"):
        print("reply.wav size:", os.path.getsize("reply.wav"))
    else:
        print("reply.wav olusmadi")

    return send_file("reply.wav", mimetype="audio/wav")


print("SERVER BASLADI")

app.run(host="0.0.0.0", port=5000)