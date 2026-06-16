import os, traceback
from fastapi import APIRouter
from Brain.brain import Brain_Hana, Log_Brain
from Brain.Mouth.mouth import Mouth_Hana
from Brain.Tecnico.hana_log import end_interaction_log
from ..schemas.chat import UserMessage
from Brain.Memory.memory_system import Save_message

HANA_KEY = os.getenv("Hana_KEY")
interacao = "terminal"

router = APIRouter()

@router.post("/chat")
async def Chat(data: UserMessage):
    user_input = data.message
    try:
        response = Brain_Hana(interacao, user_input, HANA_KEY, "terminal")
    except Exception as e:
        print(f"LOG -> {e}")
        traceback.print_exc()
        return {
            "tool": e,
            "response": e
        }
    Hana = response['prompt']
    tool = response['tool']
    
    if tool == "yes":
        return {
            "tool": "yes"
        }
    else:
        Hana_response = await Mouth_Hana(messages=Hana, terminal="on")
        Log_Brain(interacao, 'RESPONSE_TUPLE', "TUPLE", {"Resposta": Hana_response})
        Save_message(role="user", content=f"[USER_MESSAGE] - {user_input}") 
        Save_message(role="user", content=f"[ASSISTANT_MESSAGE] - {Hana_response['resposta']}") 
        end_interaction_log("Logs/hana_brain.jsonl")
        return {
            "tool": tool,
            "response": Hana_response['resposta']
        }
    