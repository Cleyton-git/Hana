import logging
from datetime import datetime
import json
import os

logger = logging.getLogger("Hana")
logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)

file = logging.FileHandler("hana_debug.log", encoding="utf-8")
file.setLevel(logging.INFO)

logger.addHandler(console)
logger.addHandler(file)

def HIPOCAMPO_file_log(stage: str, data: dict):
    payload = {
        "module": "HIPOCAMPO",
        "stage": stage,
        "data": data
    }

    logger.info(json.dumps(payload, ensure_ascii=False))

def Token_log(model, usage, func):

    payload = {
        "timestamp": str(datetime.now()),
        "model": model,
        "function": func,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0)
    }
    
    with open("Brain/tokens.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        
def Hana_console(msg):
    logger.warning(msg)