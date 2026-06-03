import os, requests
from fastapi import APIRouter, Request
from Brain.brain import Brain_Hana, Log_Brain
from Brain.Mouth.mouth import Mouth_Hana
from Brain.Tecnico.hana_log import end_interaction_log
from ..schemas.chat import UserMessage

HANA_KEY = os.getenv("Hana_KEY")
TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")
interacao = "telegram"

router = APIRouter()

@router.post("/telegram")
async def Telegram(request: Request):
    try:
        data = await request.json()
        id_chat = data['message']['chat']['id']
        user_input = data['message']['text']
    
        response = Brain_Hana(interacao, user_input, HANA_KEY, "telegram")
        Hana = response['prompt']
        memory = response['memory']
        tool = response['tool']
        
        if tool == "yes":
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage", 
                        data = {
                            "chat_id": id_chat,
                            "text": "Hana detectou um tool"
                        })
            return {"ok": True}
        else:
        Hana_response = await Mouth_Hana(msg=Hana, terminal="off")
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage", 
                     data = {
                         "chat_id": id_chat,
                         "text": Hana_response["resposta"]
                     })
        Log_Brain(interacao, 'RESPONSE_TUPLE', "TUPLE", {"Resposta": Hana_response})
        end_interaction_log("Logs/hana_brain.jsonl")
        return {"ok": True}
    except Exception as e:
        print(f"LOG -> ERRO: {e}")
        return {"ok": True}
        
        