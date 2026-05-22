import keyboard
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from ..Tecnico.hana_log import Hana_console, Hana_log

fs = 16000
audio_data = []
#model = WhisperModel(
#        "medium",
#        device="cpu",
#        compute_type="int8"
#    )

def Fala_Pai():
    while True:
        print("Esperando a tecla V ser pressionada...")

        keyboard.wait("v")

        Hana_log("🎙 Gravando...")

        audio_data = []

        def callback(indata, frames, time, status):
            audio_data.append(indata.copy())

        stream = sd.InputStream(
            samplerate=fs,
            channels=1,
            callback=callback
        )

        stream.start()

        while keyboard.is_pressed("v"):
            pass

        stream.stop()
        stream.close()

        Hana_log("🛑 Gravação encerrada.")

        import numpy as np

        audio = np.concatenate(audio_data, axis=0)

        write("audio.wav", fs, audio)

        print("🧠 Transcrevendo...")

        segments, info = model.transcribe("audio.wav", language="pt")

        texto = ""

        for segment in segments:
            texto += segment.text

        return texto
        