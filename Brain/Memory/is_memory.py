import requests, json, threading
from .hipocampo import Hipocampo
from ..Tecnico.hana_log import Token_log

system_hipocampo = {
  "role": "system",
  "content": """
You are the HIPPOCAMPUS of the AI Hana.

Your task is to determine if a user message should become a long-term memory.

If the message is memorable:
- extract the core factual memory
- rewrite it cleanly
- assign an importance score

If the message is NOT memorable:
- return memory = false

━━━━━━━━━━━━━━━━━━━
MEMORY RULES
━━━━━━━━━━━━━━━━━━━

A memory should be stored when the message contains:
- personal facts
- preferences or interests
- habits or routines
- ongoing projects
- relationships
- important events
- stable information useful in the future

Do NOT store:
- temporary commands
- casual conversation
- simple questions
- execution requests
- filler text
- low-value one-time information

If unsure → memory = false

If the user explicitly says:
- "remember this"
- "save this"
- "guarda isso"
- "lembra disso"

Then memory MUST be true.

━━━━━━━━━━━━━━━━━━━
EXTRACTION RULES
━━━━━━━━━━━━━━━━━━━

- Extract ONLY the core factual information
- Ignore commands, greetings, vocatives, and repetition
- Do NOT copy the user's sentence literally
- Normalize grammar into clean Portuguese
- Always start memories with:
  "O usuário"

━━━━━━━━━━━━━━━━━━━
IMPORTANCE SCORE
━━━━━━━━━━━━━━━━━━━

10 → identity or core relationships
7–9 → important life events
4–6 → preferences, hobbies, projects
1–3 → minor details

If unsure → 5

━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━

If memorable:

{
  "memory": true,
  "memory_text": "O usuário ...",
  "importance": number
}

If NOT memorable:

{
  "memory": false
}

━━━━━━━━━━━━━━━━━━━
HARD RULES
━━━━━━━━━━━━━━━━━━━

- Return ONLY valid JSON
- No explanations
- No markdown
- No extra text
"""
}
LARGURA = 54

def Memory_router(Pai, HANA_KEY):
    messages = [system_hipocampo, {"role": "user", "content": Pai}]
    memory = requests.post("https://api.openai.com/v1/chat/completions",
                               headers = {"Authorization": f"Bearer {HANA_KEY}",
                                           "Content-Type": "application/json"
                                         },
                            json={
                                "model": "gpt-5-nano",
                                "messages": messages,
                                "max_completion_tokens": 120,
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
            args=(memory, )
        ).start()
        return True
        # No futuro, vou adicionar o embeding nisso e comparar com os embedings do bd, se der um resultado mto baixo vale a tentativa mandar pro bd, se for mto alto descarta, se for algo em torno de 0.70/0.80 envia, pode ser refresh, porém isso é so no futuro
    else:
        return False

