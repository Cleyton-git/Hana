import logging
from datetime import datetime
import json
import os

logger = logging.getLogger("Hana")
logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.WARNING)

file = logging.FileHandler("LOGS/Hipocampo.log", encoding="utf-8")
file.setLevel(logging.INFO)

logger.addHandler(console)
logger.addHandler(file)

def Log_Brain(interaction: int, module: str, stage: str, data: dict):
    entry = {
        "interaction": interaction,
        "timestamp": datetime.utcnow().isoformat(),
        "module": module,
        "stage": stage,
        "data": data
    }

    with open("Logs/hana_brain.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry

def end_interaction_log(log):
    with open(log, "a", encoding="utf-8") as f:
        f.write("FIM DA INTERAÇÃO\n")

def Log_Tool(interacao, input_text, tool_name, result="executed"):
    log_entry = {
        "interaction": interacao,
        "timestamp": datetime.utcnow().isoformat(),
        "module": "TOOL",
        "data": {
            "input": input_text,
            "tool": tool_name,
            "result": result
        }
    }

    line = json.dumps(log_entry, ensure_ascii=False)

    with open("Logs/Tools.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")

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
    
    with open("LOGS/tokens.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        
def Hana_console(msg):
    logger.warning(msg)