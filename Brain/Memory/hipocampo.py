import json, textwrap, asyncio, requests, os
from Brain.Memory.memory_system import Save_memory, Get_memorys_ids, Update_memory, Get_memorys_by_entity
import numpy as np
from ..Tecnico.hana_log import HIPOCAMPO_file_log, end_interaction_log
from ..Mouth.mouth import Ia_duplicy_verification, Criar_frase
from datetime import datetime
from playsound3 import playsound
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_KEY = os.getenv("TELEGRAM_KEY")

def Hipocampo(memoria, mode):
    memoria['entity'] = memoria['entity'].lower()
    HIPOCAMPO_file_log("BEGIN", {"NEW_MEMORY": memoria, "TIME": datetime.now().isoformat()})
    cortex_orbito_frontal_resp = Cortex_Orbitofrontal(memoria)
    HIPOCAMPO_file_log("CORTEX_ORBITO_FRONTAL", {"valid": cortex_orbito_frontal_resp})
    if cortex_orbito_frontal_resp == "ok":
      response = Reconsolidacao(memoria)
      if Reconsolidacao == "ignore":
        HIPOCAMPO_file_log("RECONSOLIDATION_END_PREMATURE", {"status": "UNSAVED", "reasoning": "memoria identica"})
        return
      HIPOCAMPO_file_log("RECONSOLIDATION", {"status": "ok"})
      Memoria_associativa(memoria, response['old_memorias'], mode)
    end_interaction_log("Logs/Hipocampo.log")
  
def Cortex_Orbitofrontal(memoria):
  if not isinstance(memoria.get("importance"), int): # ve se a memoria vem com importance
    HIPOCAMPO_file_log("END_CORTEX_ORBITO_FRONTAL", {"REASON": "ERRO NO IMPORTANCE"})
    return "NOT"
  if "O usuário" not in memoria['memory_text']: # Ve se a memoria tem "O usuario"
    HIPOCAMPO_file_log("END_CORTEX_ORBITO_FRONTAL", {"REASON": "MEMORIA NÃO TEM O USUARIO"})
    return "NOT"
  return "ok"

def Reconsolidacao(memoria):
  HIPOCAMPO_file_log("RECONSOLIDATION", { "status": "running"})
  memorias = [mem[1] for mem in Get_memorys_ids()]
  for c in memorias:
    if memoria['memory_text'] == c:
      return "ignore"
  old_memorias = Get_memorys_by_entity(memoria['entity'])
  return {
    'old_memorias': old_memorias,
  }

def Memoria_associativa(new_memoria, old_memorias, mode):
  if len(old_memorias) == 0:
    Save_memory(memory=new_memoria['memory_text'], importance=new_memoria['importance'], entity=new_memoria['entity'])
    HIPOCAMPO_file_log("MEMORIA_AFETIVA_END_PREMATURE", { "status": "SAVED", "reasoning": "new memory detected"})
    if mode == "terminal":
      asyncio.run(Criar_frase(f"Rana criou uma nova memoria {new_memoria['memory_text']}, entidade {new_memoria['entity']}", "audios/new_memory.mp3"))
      playsound("audios/new_memory.mp3")
    elif mode == "telegram":
      requests.post(f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage", 
                     data = {
                         "chat_id": "7866829741",
                         "text": f"Hana criou uma nova memoria {new_memoria['memory_text'].lower()}, entidade {new_memoria['entity']}"
                     })
    return "new"
  decisions = []
  for id, memory, entity, importance in old_memorias:
    system_check_duplicidade = {
    "role": "system",
    "content": """
  Você é o HIPOCAMPO de um sistema de memória de uma IA.

  Sua função é comparar duas memórias e decidir a relação semântica entre elas.

  Você NÃO deve julgar relevância geral.
  Você NÃO deve filosofar.
  Você NÃO deve recusar casos ambíguos.
  Você deve apenas classificar a relação entre memory_a e memory_b.

  ---

  MEMÓRIAS:

  - memory_a = memória existente no banco
  - memory_b = nova memória a ser avaliada

  ---

  TAREFA:

  Classifique a relação entre as duas memórias usando APENAS UMA ação final.

  ---

  SAÍDA OBRIGATÓRIA (JSON):

  {
    "action": "duplicate | refresh | new | replace",
    "merged_memory": "string"
  }

  ---

  DEFINIÇÕES DAS AÇÕES:

  1. duplicate
  → Mesma informação, sem valor adicional
  → memory_b não adiciona nada novo

  2. refresh
  → Mesma ideia central, mas memory_b adiciona informação útil
  → Deve gerar merged_memory atualizado

  3. new
  → Fatos diferentes ou não relacionados semanticamente
  → Não existe relação direta entre memory_a e memory_b

  4. replace
  → memory_b contradiz memory_a ou substitui completamente a informação anterior
  (ex: opinião mudou, gosto mudou, estado mudou)

  ---

  REGRAS IMPORTANTES:

  - Nunca retorne mais de uma action
  - Nunca invente fatos
  - merged_memory só deve existir quando fizer sentido (refresh ou replace)
  - Seja consistente e determinístico
  - Se houver dúvida entre duplicate e refresh, prefira refresh
  - Se houver contradição clara, use replace
  - Se não houver relação clara, use new

  ---

  EXEMPLOS:

  A: "O usuário gosta de beber água"
  B: "O usuário bebe bastante água ao longo do dia"

  → {
    "action": "refresh",
    "merged_memory": "O usuário gosta de beber água e costuma beber bastante água ao longo do dia"
  }

  ---

  A: "O usuário gosta de beber água"
  B: "O usuário não gosta de beber água"

  → {
    "action": "replace",
    "merged_memory": "O usuário não gosta de beber água"
  }

  ---

  A: "O usuário tem um cachorro chamado Bilu"
  B: "O usuário gosta de jogar videogame"

  → {
    "action": "new",
    "merged_memory": ""
  }

  ---

  A: "O usuário gosta de água"
  B: "O usuário gosta de água"

  → {
    "action": "duplicate",
    "merged_memory": ""
  }

  ---

  Responda APENAS com JSON válido.
  """
  }
    msg = [
        system_check_duplicidade,
        {
            "role": "user",
            "content": json.dumps({
                "memory_a": memory,
                "memory_b": new_memoria['memory_text']
            })
          }
      ]
    decision = Ia_duplicy_verification(msg=msg, model="llama3.1:8b")
    decisions.append({
      "id": id,
      "candidate": memory,
      "decision": decision
    })
  HIPOCAMPO_file_log("MEMORIA_ASSOCIATIVA_CANDIDATOS", {"Candidatos": f"{decisions}"})

  for item in decisions:
    id = item['id']
    action = item["decision"]["action"]
    
    if action == "refresh":
      HIPOCAMPO_file_log("STATUS_REFRESH", {"new_memory": new_memoria['memory_text'], "Old_memory": item['candidate']})
      Update_memory(mem_id=id, new_memory=new_memoria['memory_text'], entity=new_memoria['entity'], importance=new_memoria['importance'])
      if mode == "terminal":
        asyncio.run(Criar_frase(f"Rana atualizou uma memoria memoria antiga ID: {id}, nova memoria: {new_memoria['memory_text']}", "audios/refresh_memory.mp3"))
        playsound("audios/refresh_memory.mp3")
      elif mode == "telegram":
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage", 
                     data = {
                         "chat_id": "7866829741",
                         "text": f"Hana atualizou uma memoria memoria antiga ID: {id}, nova memoria: {new_memoria['memory_text'].lower()}"
                     })
      Memoria_console("REFRESH", new_memoria['memory_text'])
      return "refresh"
  
  for item in decisions:
    id = item['id']
    action = item["decision"]["action"]
    
    if action == "replace":
      HIPOCAMPO_file_log("STATUS_REPLACE", {"new_memory": new_memoria['memory_text'], "Old_memory": item['candidate']})
      Update_memory(mem_id=id, new_memory=new_memoria['memory_text'], entity=new_memoria['entity'], importance=new_memoria['importance'])
      if mode == "terminal":
        asyncio.run(Criar_frase(f"Rana atualizou uma memoria memoria antiga ID: {id}, nova memoria: {new_memoria['memory_text']}", "audios/refresh_memory.mp3"))
        playsound("audios/refresh_memory.mp3")
      elif mode == "telegram":
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage", 
                     data = {
                         "chat_id": "7866829741",
                         "text": f"Hana atualizou uma memoria memoria antiga ID: {id}, nova memoria: {new_memoria['memory_text'].lower()}"
                     })
      Memoria_console("REPLACE", new_memoria['memory_text'])
      return "refresh"
  
  for item in decisions:
    action = item["decision"]["action"]
    if action == "new":
      HIPOCAMPO_file_log("STATUS_NEW", {"new_memory": new_memoria['memory_text']})
      Save_memory(memory=new_memoria['memory_text'], importance=new_memoria['importance'], entity=new_memoria['entity'])
      if mode == "terminal":
        asyncio.run(Criar_frase(f"Rana criou uma nova memoria {new_memoria['memory_text']}, entidade {new_memoria['entity']}", "audios/new_memory.mp3"))
        playsound("audios/new_memory.mp3")
      elif mode == "telegram":
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage", 
                     data = {
                         "chat_id": "7866829741",
                         "text": f"Hana criou uma nova memoria {new_memoria['memory_text'].lower()}, entidade {new_memoria['entity']}"
                     })
      Memoria_console("NEW", new_memoria['memory_text'])
      return "new"
  
  for item in decisions:
    action = item["decision"]["action"]
    if action == "duplicate":
      HIPOCAMPO_file_log("STATUS_DUPLICATE", {"new_memory": new_memoria['memory_text']})
      Memoria_console("DUPLICATE", new_memoria['memory_text'])
      return "ignore"
    
    
def cosine(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def Memoria_console(status, memoria):
    largura = 60
    inner = largura - 2

    label = "DATA   | "
    wrap_size = inner - len(label)

    wrap_size = max(10, wrap_size)

    linhas = textwrap.wrap(str(memoria), width=wrap_size)

    def line(txt=""):
        txt = str(txt)
        return "║" + txt[:inner].ljust(inner) + "║"

    print("\n╔" + "═" * inner + "╗")
    print(line(f"{status}".center(inner)))
    print("╠" + "═" * inner + "╣")

    if linhas:
        print(line(label + linhas[0]))

        for l in linhas[1:]:
            print(line(" " * len(label) + l))

    print("╚" + "═" * inner + "╝")
