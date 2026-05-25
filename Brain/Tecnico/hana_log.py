import logging
from datetime import datetime
import json
import textwrap

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
        
def Hana_console(msg):
    logger.warning(msg)