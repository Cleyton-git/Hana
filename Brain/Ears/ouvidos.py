import keyboard
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
import textwrap

LARGURA = 54
fs = 16000
audio_data = []
#model = WhisperModel(
#        "medium",
#        device="cpu",
#        compute_type="int8"
#    )

def Fala_Pai():
    while True:
        linha("AUDIO    | Esperando ativação [V]...")

        keyboard.wait("v")

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

        import numpy as np

        audio = np.concatenate(audio_data, axis=0)

        write("audio.wav", fs, audio)

        segments, info = model.transcribe("audio.wav", language="pt")

        texto = ""

        for segment in segments:
            texto += segment.text
            
        linha(f"STT      | {texto}")

        return texto
        
def linha(texto):
    linhas = textwrap.wrap(
        str(texto),
        width=LARGURA
    )
    for l in linhas:
        print(f"║ {l:<{LARGURA}} ║")