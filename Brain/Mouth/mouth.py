import requests, os, edge_tts, json, asyncio
from playsound3 import playsound
from dotenv import load_dotenv
from ..Tecnico.hana_log import Token_log
from ..Agents.agent_requests import Talking_Agent

load_dotenv()
HANA_KEY = os.getenv("Hana_KEY")

async def Criar_frase(texto, path_save):
  communicate = edge_tts.Communicate(
        texto,
        voice="pt-BR-FranciscaNeural",
        pitch="+5Hz",
        rate="+8%"
    )

  await communicate.save(path_save)
  
async def Mouth_Hana(messages, terminal):
  response = Talking_Agent(HANA_KEY, model="gpt-5-nano", messages=messages, completion_tokens=5000, AGENTE="MOUTH_HANA")
  response = response['response']
  
  if terminal == "on":
    await Criar_frase(response, "audios/Hana_voz.mp3")
    playsound("audios/Hana_voz.mp3")
    
  return {"resposta": response}


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

