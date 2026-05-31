import os
from fastapi import APIRouter
from Brain.brain import Brain_Hana, Log_Brain
from Brain.Mouth.mouth import Mouth_Hana
from Brain.Tecnico.hana_log import end_interaction_log
from ..schemas.chat import UserMessage

HANA_KEY = os.getenv("Hana_KEY")
interacao = "web"

router = APIRouter()

@router.post("/chat")
async def Chat(data: UserMessage):
    user_input = data.message
    Hana = Brain_Hana(interacao, user_input, HANA_KEY)
    if Hana == "stop":
        return
    else:
        Hana_response = await Mouth_Hana(Hana)
        Log_Brain(interacao, 'RESPONSE_TUPLE', "TUPLE", {"Resposta": Hana_response})
        end_interaction_log("Logs/hana_brain.jsonl")
    