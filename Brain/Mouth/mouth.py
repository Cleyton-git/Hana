import requests
import json
import edge_tts
import asyncio
from playsound3 import playsound

async def Criar_frase(texto):
  communicate = edge_tts.Communicate(
        texto,
        voice="pt-BR-FranciscaNeural",
        pitch="+5Hz",
        rate="+8%"
    )

  await communicate.save("voz.mp3")
  
def Mouth_Hana(url, msg, model):
    r = requests.post(
      url,
        json={
          "model": model,
          "messages": msg,
          "stream": False,
          
        }
    )
    
    r = r.json()["message"]["content"]
    asyncio.run(Criar_frase(r))
    playsound("voz.mp3")
    return r


def Ia_duplicy_verification(msg, model):
    r = requests.post(
      "http://127.0.0.1:11434/api/chat",
        json={
          "model": model,
          "messages": msg,
          "stream": False,
          "temperature": 0
        }
    )

    return json.loads(r.json()["message"]["content"])

