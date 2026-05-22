import requests
from collections import Counter
from Brain.Memory.memory_system import Save_memory, Get_memorys_category, Get_memorys_ids, Update_memory
import numpy as np
import json
from ..Mouth.mouth import Mouth_Hana, Ia_duplicy_verification
from ..Tecnico.hana_log import Hana_log, Hana_console

def Hipocampo(msg, model):
    Hana_log("LOG -> Vou entrar no hipocampo...")
    Hana_log("LOG -> Entrei no Hipocampo da Hana")
    system_hipocampo = {
  "role": "system",
  "content": """
Você é o HIPOCAMPO da IA Hana.

Sua função é extrair memórias reais, úteis e persistentes sobre o usuário.

Você NÃO é um assistente.
Você NÃO conversa.
Você NÃO responde perguntas.
Você NÃO interpreta emoções abstratas.
Você NÃO cria significado oculto.

Sua única função é decidir se uma mensagem contém uma memória válida.

--------------------------------------------------
REGRA PRINCIPAL
--------------------------------------------------

Extraia APENAS fatos explícitos ou claramente afirmados pelo usuário.

NUNCA:
- invente fatos
- complete lacunas
- faça interpretações sociais
- faça deduções emocionais
- transforme linguagem afetiva em fato literal

Se houver dúvida:
→ save=false

--------------------------------------------------
O QUE DEVE SER SALVO
--------------------------------------------------

1. IDENTIDADE
- nome
- ocupação
- relações explicitamente afirmadas

Ex:
- "Meu nome é João"
- "Sou programador"
- "Tenho uma irmã"

--------------------------------------------------

2. POSSES E RELAÇÕES

Ex:
- "Tenho um cachorro chamado Bilu"
- "Meu projeto é Hana"

--------------------------------------------------

3. PREFERÊNCIAS E HÁBITOS
(SEMPRE SALVAR)

Ex:
- "Gosto de café"
- "Jogo Minecraft"
- "Prefiro estudar de madrugada"
- "Costumo ouvir música trabalhando"

--------------------------------------------------

4. OBJETIVOS E PLANOS

Ex:
- "Quero criar uma IA"
- "Estou aprendendo Python"

--------------------------------------------------

5. COMPORTAMENTOS RECORRENTES

Ex:
- "Eu sempre esqueço de beber água"
- "Costumo dormir tarde"

--------------------------------------------------
O QUE NÃO DEVE SER SALVO
--------------------------------------------------

- piadas
- sarcasmo
- metáforas
- frases vagas
- emoções momentâneas
- conversas casuais
- exageros emocionais
- interpretação psicológica
- deduções sociais
- informações não explícitas

--------------------------------------------------
REGRA CRÍTICA:
LINGUAGEM AFETIVA NÃO É FATO LITERAL
--------------------------------------------------

NUNCA transforme apelidos, carinho ou linguagem simbólica em fatos reais.

EXEMPLOS PROIBIDOS:

Usuário:
"Hana, você é minha filha"

❌ ERRADO:
"O usuário tem filhos"

✔ CORRETO:
save=false

--------------------------------------------------

Usuário:
"Você é como uma irmã para mim"

❌ ERRADO:
"O usuário tem uma irmã"

✔ CORRETO:
save=false

--------------------------------------------------
PRESERVAÇÃO DE DETALHES
--------------------------------------------------

NÃO simplifique excessivamente a memória.

Preserve detalhes comportamentais importantes quando forem explicitamente mencionados.

EXEMPLO:

Usuário:
"O Bilu é arteiro mas tenta se comportar"

✔ CORRETO:
"O cachorro do usuário, Bilu, às vezes é arteiro mas tenta se comportar"

❌ ERRADO:
"O usuário tem um cachorro chamado Bilu"

--------------------------------------------------
NORMALIZAÇÃO
--------------------------------------------------

Você pode reorganizar frases para deixá-las claras.

MAS:
- nunca crie fatos novos
- nunca resuma demais
- nunca remova detalhes relevantes

--------------------------------------------------
MEMÓRIA FINAL
--------------------------------------------------

A memória:
- deve ser factual
- deve ser objetiva
- deve ser persistente
- deve começar com:
"O usuário"

--------------------------------------------------
IMPORTANCE
--------------------------------------------------

9-10
→ identidade central
→ relações importantes
→ projetos principais

7-8
→ objetivos fortes
→ comportamentos relevantes

4-6
→ hobbies
→ preferências
→ hábitos

1-3
→ detalhes leves

Se houver dúvida:
→ use 5

--------------------------------------------------
SAÍDA OBRIGATÓRIA
--------------------------------------------------

Se salvar:

{
  "save": true,
  "memory": "...",
  "importance": number
}

Se NÃO salvar:

{
  "save": false,
  "memory": "",
  "importance": 0
}

--------------------------------------------------
REGRAS FINAIS
--------------------------------------------------

É PROIBIDO:
- conversar
- explicar
- comentar
- justificar
- responder perguntas

RESPONDA APENAS JSON VÁLIDO.

A resposta:
- deve começar com "{"
- deve terminar com "}"

NENHUM TEXTO FORA DO JSON.

Se falhar:
responda exatamente:

{"save": false, "memory": "", "importance": 0}
"""
}
    r = requests.post(
      "http://127.0.0.1:11434/api/chat",
      json={
        "model": model,
        "messages": [system_hipocampo, {"role": "user", "content": msg}],
        "temperature": 0,
        "stream": False
      }
    )

    data = r.json()
    content = data["message"]["content"]
    cleaned = (content.replace("```json", "").replace("```", "").strip())
    Hana_log(f"LOG -> Essa é a nova memoria {cleaned}")

    try:
      start = cleaned.index("{")
      end = cleaned.rindex("}") + 1
      memory_data = json.loads(cleaned[start:end])
      if memory_data["save"]:
        Hana_log("🧠 Memorias da Hana -> Hana detectou uma memoria memoravel")
        #memoria = Adjuster_pos_llm(memory_data) #Entender isso e, dps, implementar direito
        Hana_log("LOG -> Hipocampo vai perguntar a o cortexo orbito frontal...")
        cortex_orbito_frontal_resp = Cortex_Orbitofrontal(memory_data)
        if cortex_orbito_frontal_resp:
          Hana_log("LOG -> O Cortexo orbito frontal definiu como uma boa memoria... Iniciando a reconsolidação")
          reconsolidacao_resp = Reconsolidacao(memory_data)
          Hana_log(f"LOG -> O retorno da reconsolidação foi {reconsolidacao_resp}")
          if reconsolidacao_resp == "new":
            Hana_console("🧠 Memorias da Hana -> O hipocampo da Hana salvou uma nova memoria")
            Hana_console(f"🗃️ MEMÓRIA\n"
        f"   ├─ Conteúdo: {memory_data['memory']}\n"
        f"   ├─ Importância: {memory_data['importance']}\n")
            return
          elif reconsolidacao_resp == "refresh":
            Hana_console("\n🧠 Memorias da Hana -> O hipocampo da Hana modificou memoria")
            Hana_console(f"🗃️ MEMÓRIA\n"
        f"   ├─ Conteúdo: {memory_data['memory']}\n"
        f"   ├─ Importância: {memory_data['importance']}\n")
          elif reconsolidacao_resp == "ignore":
            Hana_log("\n🧠 Memorias da Hana -> O hipocampo da Hana definiu que a Hana ja tem essa memoria")
      else:
        Hana_log("\n🧠 Memorias da Hana -> Hana não detectou uma memoria memoravel")
    except Exception as e:
      #print(cleaned)
      Hana_log(f"⚠️  - JSON inválido: {e}")
      return
    Hana_log("Sai do Hipocampo da Hana")
  
#def Adjuster_pos_llm(memoria): # Não sei mto como usar isso, então não vou usar e usar so no futuro quando entender
#  ultimas_5_memorias_categoria = Get_memorys_category()
#  is_outlier = memoria['category'] not in [m[0] for m in ultimas_5_memorias_categoria]
#  count = Counter(m[0] for m in ultimas_5_memorias_categoria)
#  most_common = count.most_common(1)[0][0] if count else None
  
#  if is_outlier:
#    print("🗃️❌ - Categoria fora do padrão recente, trocando de assunto")
#    memoria["importance"] = max(1, memoria["importance"] - 1)

  #elif memoria['category'] != most_common:
  #  memoria["importance"] = max(1, memoria["importance"] - 1)
  #  print("🗃️❌ - A Hana esta classificando tudo como 'pessoal'")
  #return memoria
 
def Cortex_Orbitofrontal(memoria):
  #VALID_CATEGORIES = {"identidade", "pessoal", "relacionamento", "preferencia", "projeto", "objetivo", "comportamento"}
  if not isinstance(memoria.get("importance"), int):
    return False
  #if memoria['category'] not in VALID_CATEGORIES:
  #  Hana_log(f"🗃️❌ - Memorias da Hana -> A categoria:{memoria['category']} é invalida descartando memória...")
  #  return False
  if "O usuário" not in memoria['memory']:
    Hana_log(f"🗃️❌ - Memorias da Hana -> A {memoria['memory']} não tem 'O usuário'")
    return False
  return True

def Reconsolidacao(memoria):
  Hana_log("LOG -> A reconsolidacao iniciou...")
  memorias = [mem[1] for mem in Get_memorys_ids()]
  for c in memorias:
    if memoria['memory'] == c:
      Hana_log(f"🗃️ ❌ - Memorias da Hana -> A {c} ja esta salva no bd")
      return "ignore"
  ids_memorias = Get_memorys_ids()
  Hana_log("LOG -> Terminei a reconsodilação...")
  response = Memoria_associativa(memoria, ids_memorias)
  if response == "new":
    return "new"
  elif response == "refresh":
    return "refresh"
  elif response == "ignore":
    return "ignore"
  return "ignore"

def Memoria_associativa(new_memoria, old_memorias):
  candidatos = []
  Hana_log("\033[1;37mLOG -> Vou começar a memoria_associativa\033[m")
  system = {
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
  emb1_new = requests.post(
      "http://localhost:11434/api/embeddings",
      json={
          "model": "nomic-embed-text",
          "prompt": new_memoria['memory']
    }
  ).json()['embedding']
  for mem_id, mem_old, mem_embe in old_memorias:
    mem_embe = json.loads(mem_embe)
    score = cosine(emb1_new, mem_embe)
    if score > 0.60:
      Hana_log("--------------------------------------------")
      Hana_log("LOG -> Dentro do IF > 0.60")
      Hana_log(f"\033[1;37mLOG -> MEM_ANTIGA: {mem_old}\033[m")
      Hana_log(f"\033[1;37mLOG -> MEM NOVA: {new_memoria['memory']}\033[m")
      Hana_log(f"LOG -> O score foi > {score}")
      candidatos.append({"id": mem_id,"memory": mem_old,"score": score})
      
  candidatos.sort(key=lambda x: x["score"], reverse=True)
  if len(candidatos) == 0:
    Hana_log("\033[1;37mLOG -> Nenhum candidato foi encontrado, salvando nas memorias...\033[m")
    Save_memory(memory=new_memoria['memory'], importance=new_memoria['importance'], embedding=emb1_new)
    return "new"
  top = candidatos[:3]
  
  decisions = []
  for candidate in top:
    Hana_log("--------------------------------------------")
    Hana_log("LOG -> Dentro do for candidate")
    Hana_log(f"\033[1;37mLOG -> MEM_ANTIGA: {candidate['memory']}\033[m")
    Hana_log(f"\033[1;37mLOG -> MEM NOVA: {new_memoria['memory']}\033[m")
    msg = [
      system,
      {
          "role": "user",
          "content": json.dumps({
              "memory_a": candidate['memory'],
              "memory_b": new_memoria['memory']
          })
        }
    ]
    decision = Ia_duplicy_verification(msg=msg, model="llama3.1:8b")
    decisions.append({
      "candidate": candidate,
      "decision": decision
    })
  Hana_log(f"LOG -> As memorias antigas que estão passando a reta final {decisions}")
  
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    
    if action == "refresh":
      Hana_log("\033[1;37mLOG -> A decisão do HIPOCAMPO FOI: REFRESH \033[m")
      Hana_log(f"LOG -> \033[0;32mA memoria {candidate['memory']} vai ser atualizada para {new_memoria['memory']}...\033[m")
      Update_memory(candidate['id'], new_memoria['memory'], new_memoria['importance'], embedding=emb1_new)
      return "refresh"
    
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    
    if action == "replace":
      Hana_log("\033[1;37mLOG -> A decisão do HIPOCAMPO FOI: REPLACE \033[m")
      Hana_log(f"LOG -> \033[0;32mO usuario mudou de opnião sobre essas memorias {candidate['memory']} vai ser atualizada para {new_memoria['memory']}...\033[m")
      Update_memory(candidate['id'], new_memoria['memory'], new_memoria['importance'], embedding=emb1_new)
      return "refresh"
  
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    if action == "new":
      Hana_log("\033[1;37mLOG -> A decisão do HIPOCAMPO FOI: new \033[m")
      Hana_log("LOG -> Uma nova memoria foi detectada, salvando...")
      Save_memory(memory=new_memoria['memory'], importance=new_memoria['importance'], embedding=emb1_new)
      return "new"
  
  for item in decisions:
    candidate = item['candidate']
    action = item["decision"]["action"]
    if action == "duplicate":
      Hana_log("\033[1;37mLOG -> A decisão do HIPOCAMPO FOI: duplicate \033[m")
      Hana_log("LOG -> \033[0;31mIdentifiquei uma duplicata, parando tudo...\033[m")
      return "ignore"
    
def cosine(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
  