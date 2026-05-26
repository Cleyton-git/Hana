import requests, json, threading
from .hipocampo import Hipocampo
from ..Tecnico.hana_log import Token_log

system_memory = {
  "role": "system",
  "content": """
You are a memory classifier for the AI Hana.

Your ONLY task is to decide if a message should be stored in long-term memory.

Return ONLY valid JSON:
{"memory": true} or {"memory": false}

━━━━━━━━━━━━━━━━━━━
WHEN memory = true
━━━━━━━━━━━━━━━━━━━
Set true if the message contains:
- personal facts about the user
- preferences or interests
- habits, routines, or behavior
- ongoing projects
- relationships or important entities
- any stable information useful in the future

━━━━━━━━━━━━━━━━━━━
WHEN memory = false
━━━━━━━━━━━━━━━━━━━
Set false if the message contains:
- temporary commands or actions
- simple questions (math, trivia, requests)
- casual conversation or opinions
- execution requests (open, search, etc.)
- low-value or one-time information

━━━━━━━━━━━━━━━━━━━
HARD RULES
━━━━━━━━━━━━━━━━━━━
- If user explicitly says "remember this", ALWAYS return true
- If unsure, return false
- Output ONLY JSON. No explanation. No extra text.
"""
}
LARGURA = 54

def Memory_router(Pai, HANA_KEY):
    messages = [system_memory, {"role": "user", "content": Pai}]
    memory = requests.post("https://api.openai.com/v1/chat/completions",
                               headers = {"Authorization": f"Bearer {HANA_KEY}",
                                           "Content-Type": "application/json"
                                         },
                            json={
                                "model": "gpt-5-nano",
                                "messages": messages,
                                "max_completion_tokens": 40,
                                "response_format": {
                                        "type": "json_object"
                                        },
                                    "reasoning_effort": "minimal"
                                    },
                            )
    memory = memory.json()
    usage = memory['usage']
    Token_log(model="gpt-5-nano", usage=usage, func="HIPOCAMPO")
    memory = memory['choices'][0]["message"]["content"]
    memory = json.loads(memory)

    if memory['memory']:
        threading.Thread(
            target=Hipocampo,
            args=(Pai, HANA_KEY)
        ).start()
        return True
        # No futuro, vou adicionar o embeding nisso e comparar com os embedings do bd, se der um resultado mto baixo vale a tentativa mandar pro bd, se for mto alto descarta, se for algo em torno de 0.70/0.80 envia, pode ser refresh, porém isso é so no futuro
    else:
        return False

