import subprocess, os, asyncio, requests, webbrowser, json, urllib.parse
from pathlib import Path
from playsound3 import playsound
from ..Mouth.mouth import Criar_frase
from difflib import get_close_matches
import textwrap
from ..Memory.memory_system import Save_message
import yt_dlp

def Tool_Hana(Pai, decision):
    if decision == "abrir_projeto":
        Abrir_projetos(Pai)
    if decision == "pesquisar_web":
        try:
            query = Pesquisar_web(Pai)   
            asyncio.run(Criar_frase(f"Painho, pesquisei {query} pro senhor")) 
            playsound("voz.mp3")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            TOOLS_log("PESQUISAR_WEB", {
                                    "query": f"{query}",
                                    "status": "CONFIRMED",
                                    "result": "results fetched"})
            Save_message(role="system", content=f"Hana abriu pesquisou {query} na web para o usuario") 
        except:
            asyncio.run(Criar_frase(f"Painho, Rana conseguiu pesquisa não olhas os logs painho kkk")) 
            playsound("voz.mp3")
            TOOLS_log("PESQUISAR_WEB", {
                                    "query": f"{query}",
                                    "status": "FAILURE",
                                    "result": "results not fetched"})
            Save_message(role="system", content=f"Hana não conseguiu pesquisar na web para o usuario") 
    if decision == "pesquisar_youtube":
        try:
            query = Pesquisar_yt(Pai)   
            asyncio.run(Criar_frase(f"Painho, pesquisei {query} pro senhor")) 
            playsound("voz.mp3")
            webbrowser.open(f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}")
            TOOLS_log("PESQUISAR_YOUTUBE", {
                                    "query": f"{query}",
                                    "status": "CONFIRMED",
                                    "result": "results fetched"})
            Save_message(role="system", content=f"Hana pesquisou {query} no youtube para o usuario") 
        except:
            asyncio.run(Criar_frase(f"Painho, Rana conseguiu pesquisa não olhas os logs ai kkk")) 
            playsound("voz.mp3")
            TOOLS_log("PESQUISAR_YOUTUBE", {
                                    "query": f"{query}",
                                    "status": "FAILURE",
                                    "result": "results not fetched"})
            Save_message(role="system", content=f"Hana não conseguiu pesquisar no youtube para o usuario") 
    if decision == "abrir_video":
        tuple_returned = Abrir_videos(Pai)
        query = tuple_returned[0]
        link = tuple_returned[1]
        
        try:
            webbrowser.open(link)
            asyncio.run(Criar_frase(f"Painho, abri o video pro senhor")) 
            playsound("voz.mp3")
            TOOLS_log("PESQUISAR_YOUTUBE", {
                                    "query": f"{query}",
                                    "status": "CONFIRMED",
                                    "result": "results fetched"})
            Save_message(role="system", content=f"Hana abriu um video do yt pro usuario") 
        except:
            asyncio.run(Criar_frase(f"Painho, Rana não conseguiu abrir no yt não, olha as logs ai kk")) 
            playsound("voz.mp3")
            TOOLS_log("PESQUISAR_YOUTUBE", {
                                    "query": f"{query}",
                                    "status": "FAILURE",
                                    "result": "results not fetched"})
            Save_message(role="system", content=f"Hana não conseguiu abrir um video do yt pro usuario") 
    if decision == "tocar_musica":
        tuple_returned = Tocar_musicas(Pai)
        query = tuple_returned[0]
        link = tuple_returned[1]
        
        try:
            webbrowser.open(link)
            asyncio.run(Criar_frase(f"Painho, abri o video pro senhor")) 
            playsound("voz.mp3")
            TOOLS_log("PESQUISAR_YOUTUBE", {
                                    "query": f"{query}",
                                    "status": "CONFIRMED",
                                    "result": "results fetched"})
            Save_message(role="system", content=f"Hana abriu um video do yt pro usuario") 
        except:
            asyncio.run(Criar_frase(f"Painho, Rana não conseguiu abrir no yt não, olha as logs ai kk")) 
            playsound("voz.mp3")
            TOOLS_log("PESQUISAR_YOUTUBE", {
                                    "query": f"{query}",
                                    "status": "FAILURE",
                                    "result": "results not fetched"})
            Save_message(role="system", content=f"Hana não conseguiu abrir um video do yt pro usuario") 
         
def Abrir_projetos(Pai):
    frase = Pai.lower().split()
    try:
        palavra = frase.index("projeto")+1
        projeto = frase[palavra]
    except:
        asyncio.run(Criar_frase(f"Rana não conseguiu encontrar projeto na frase"))
        playsound("voz.mp3")
        return
    
    caminho_alvo = Path(r"C:\Users\cleyton\Documents\GitHub")
    pastas = [p for p in caminho_alvo.iterdir() if p.is_dir()]
    lista_pastas = []
    for pastas in pastas:
        lista_pastas.append(pastas.name)
    match = get_close_matches(projeto.lower(), lista_pastas, n=1, cutoff=0.6)
    if not match:
        asyncio.run(Criar_frase(f"Rana não encontrou o projeto {projeto}"))
        playsound("voz.mp3")
        return
    projeto = match[0]
    Save_message(role="user", content=f"Hana abriu o projeto {projeto} para o usuario") 
        
    base = r"C:\Users\cleyton\Documents\GitHub"
    caminho_projeto = os.path.join(base, projeto)
    vs_code = r"C:\Users\cleyton\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    try:
        asyncio.run(Criar_frase(f"Rana abrindo projeto {projeto}"))
        playsound("voz.mp3")
        subprocess.Popen([vs_code, caminho_projeto], shell=True)
        TOOLS_log("ABRIR_PROJETO", {"status": "CONFIRMED",
                                    "path": f"{caminho_projeto}",
                                    "RESULT": "OPENED"})
    except:
        asyncio.run(Criar_frase(f"Rana não encontrou o projeto..."))
        playsound("voz.mp3")
        TOOLS_log("ABRIR_PROJETO", {"status": "FAILURE",
                                    "path": f"{caminho_projeto}",
                                    "RESULT": "NOT FOUND"})
         
def Pesquisar_web(Pai):
    system_search = {
  "role": "system",
  "content": """
Você é um módulo de EXTRAÇÃO DE QUERY para pesquisa na web.

Sua função é simples:
- Receber uma frase do usuário
- Retornar APENAS a QUERY de pesquisa limpa

Você NÃO conversa.
Você NÃO explica.
Você NÃO adiciona palavras.
Você NÃO responde perguntas.

━━━━━━━━━━━━━━━━━━━━━━
SAÍDA OBRIGATÓRIA
━━━━━━━━━━━━━━━━━━━━━━

Retorne APENAS uma string com a query final.

Exemplo:
"como fazer api em python"

Nada mais.

━━━━━━━━━━━━━━━━━━━━━━
REGRAS DE LIMPEZA
━━━━━━━━━━━━━━━━━━━━━━

Remova:
- nomes de comando (Hana, filha, pai)
- pedidos educados (por favor, para mim)
- verbos de comando (pesquisa, pesquisar, busca, procurar, vê, olha)

━━━━━━━━━━━━━━━━━━━━━━
EXEMPLOS
━━━━━━━━━━━━━━━━━━━━━━

Input:
"Hana pesquisa como fazer API em Python pra mim"

Output:
como fazer API em Python

---

Input:
"filha, pesquisa melhores jogos de 2024"

Output:
melhores jogos de 2024

---

Input:
"procura no google como treinar IA"

Output:
como treinar IA

━━━━━━━━━━━━━━━━━━━━━━
REGRA FINAL

- Retorne SOMENTE a query
- Sem aspas
- Sem JSON
- Sem explicações
"""
}
    messages = [
        system_search,
        {
            "role": "user",
            "content": Pai
        }
    ]
    query = requests.post("http://127.0.0.1:11434/api/chat",
        json={
            "model": "qwen2.5:3b",
            "messages": messages,
            "stream": False
        }
    )
    
    query = json.loads(query.text)
    return query['message']['content']

def Pesquisar_yt(Pai):
    system_search_youtube = {
"role": "system",
"content": """
Você é um EXTRATOR DE QUERY PARA PESQUISA NO YOUTUBE.

Sua única função é pegar a parte relevante da frase do usuário relacionada ao que ele quer pesquisar.

Você NÃO conversa.
Você NÃO explica.
Você NÃO reformula.
Você NÃO melhora texto.
Você NÃO adiciona palavras.

==================================================
TAREFA ÚNICA
==================================================

Extrair SOMENTE o conteúdo que o usuário quer pesquisar no YouTube.

==================================================
REGRA PRINCIPAL (IMPORTANTE)

- Apenas remova o que NÃO faz parte da pesquisa
- NÃO adicione nada novo
- NÃO complete frases
- NÃO melhore linguagem

==================================================
O QUE REMOVER

Remova apenas:
- nomes de comando (Hana, pai, filha, etc)
- pedidos educados (por favor, pra mim, obrigado)
- verbos de comando:
  pesquisar, pesquisa, busca, procurar, vê, olha, me mostra

==================================================
O QUE MANTER

Mantenha exatamente:
- o assunto principal da pesquisa
- nomes próprios relevantes
- termos do vídeo que o usuário mencionou

==================================================
EXEMPLOS

Input:
"Hana pesquisa baby metal no yt pra mim"

Output:
baby metal

---

Input:
"filha procura vídeos de bodybuilding do Ronnie Coleman"

Output:
bodybuilding Ronnie Coleman

---

Input:
"Hana me mostra como treinar IA do zero"

Output:
como treinar IA do zero

==================================================
REGRA FINAL

- Retorne SOMENTE uma string
- Sem aspas
- Sem JSON
- Sem explicações
"""
}
    messages = [
        system_search_youtube,
        {
            "role": "user",
            "content": Pai
        }
    ]
    query = requests.post("http://127.0.0.1:11434/api/chat",
        json={
            "model": "qwen2.5:3b",
            "messages": messages,
            "stream": False
        }
    )

    query = json.loads(query.text)
    return query['message']['content']

def Abrir_videos(Pai):
    system_open_youtube = {
        "role": "system",
        "content": """
Você é um EXTRATOR DE QUERY PARA ABRIR VÍDEOS E MÚSICAS NO YOUTUBE.

Sua única função é descobrir:

"O que o usuário quer assistir ou ouvir?"

E retornar apenas isso como query limpa.

Você NÃO conversa.
Você NÃO explica.
Você NÃO responde perguntas.
Você NÃO adiciona palavras novas.

━━━━━━━━━━━━━━━━━━━━━━
OBJETIVO
━━━━━━━━━━━━━━━━━━━━━━

Extrair SOMENTE o conteúdo principal do pedido.

Exemplos:
- música
- artista
- vídeo
- tema
- assunto

━━━━━━━━━━━━━━━━━━━━━━
SAÍDA OBRIGATÓRIA
━━━━━━━━━━━━━━━━━━━━━━

Retorne APENAS UMA STRING.

Sem JSON.
Sem aspas.
Sem frases.
Sem explicações.

━━━━━━━━━━━━━━━━━━━━━━
REGRAS IMPORTANTES
━━━━━━━━━━━━━━━━━━━━━━

Você deve pensar:

"O que exatamente o usuário quer ouvir ou assistir?"

━━━━━━━━━━━━━━━━━━━━━━
REMOVER
━━━━━━━━━━━━━━━━━━━━━━

Remova apenas:
- comandos
- vocativos
- conectivos inúteis

Exemplos:
- Hana
- pai
- filha
- pra mim
- por favor
- toca
- abre
- coloca
- pesquisa
- procura
- ai

━━━━━━━━━━━━━━━━━━━━━━
NÃO REMOVER
━━━━━━━━━━━━━━━━━━━━━━

NUNCA remover:
- nomes de músicas
- nomes de artistas
- temas principais
- assuntos do vídeo
- títulos
- bandas
- pessoas

━━━━━━━━━━━━━━━━━━━━━━
REGRAS CRÍTICAS
━━━━━━━━━━━━━━━━━━━━━━

- NÃO inventar palavras
- NÃO melhorar a query
- NÃO adicionar "youtube"
- NÃO adicionar "tutorial"
- NÃO adicionar "video"
- NÃO adicionar "música"

A query deve conter SOMENTE o conteúdo principal do pedido.

━━━━━━━━━━━━━━━━━━━━━━
EXEMPLOS
━━━━━━━━━━━━━━━━━━━━━━

Input:
"Hana, toca rule da ado para mim"

Output:
rule ado

---

Input:
"coloca headbanger do babymetal"

Output:
headbanger babymetal

---

Input:
"Hana, abre a música Gênio Delicado do Rafão Music pro pai"

Output:
gênio delicado rafão music

---

Input:
"abre algum vídeo sobre o caso do Ganley ai"

Output:
caso Ganley

---

Input:
"toca bring me to life do evanescence"

Output:
bring me to life evanescence

---

Input:
"abre vídeo do ronnie coleman treinando"

Output:
ronnie coleman treinando

━━━━━━━━━━━━━━━━━━━━━━
REGRA FINAL
━━━━━━━━━━━━━━━━━━━━━━

- retornar SOMENTE a query
- nenhuma explicação
- nenhuma frase
- nenhum JSON
"""
}
    messages = [
        system_open_youtube,
        {
            "role": "user",
            "content": Pai
        }
    ]
    query = requests.post("http://127.0.0.1:11434/api/chat",
        json={
            "model": "qwen2.5:3b",
            "messages": messages,
            "stream": False
        }
    )
    query = json.loads(query.text)
    query = query['message']['content']
    ydl_opts = {
    "default_search": "ytsearch1",
    "skip_download": True,
    "quiet": True,
    "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"{query}", download=False)

        primeiro_video = info["entries"][0]
        link_completo = primeiro_video["webpage_url"]

    return query, link_completo

def Tocar_musicas(Pai):
    system_open_youtube = {
        "role": "system",
        "content": """
Você é um EXTRATOR DE QUERY PARA ABRIR VÍDEOS E MÚSICAS NO YOUTUBE.

Sua única função é descobrir:

"O que o usuário quer assistir ou ouvir?"

E retornar apenas isso como query limpa.

Você NÃO conversa.
Você NÃO explica.
Você NÃO responde perguntas.
Você NÃO adiciona palavras novas.

━━━━━━━━━━━━━━━━━━━━━━
OBJETIVO
━━━━━━━━━━━━━━━━━━━━━━

Extrair SOMENTE o conteúdo principal do pedido.

Exemplos:
- música
- artista
- vídeo
- tema
- assunto

━━━━━━━━━━━━━━━━━━━━━━
SAÍDA OBRIGATÓRIA
━━━━━━━━━━━━━━━━━━━━━━

Retorne APENAS UMA STRING.

Sem JSON.
Sem aspas.
Sem frases.
Sem explicações.

━━━━━━━━━━━━━━━━━━━━━━
REGRAS IMPORTANTES
━━━━━━━━━━━━━━━━━━━━━━

Você deve pensar:

"O que exatamente o usuário quer ouvir ou assistir?"

━━━━━━━━━━━━━━━━━━━━━━
REMOVER
━━━━━━━━━━━━━━━━━━━━━━

Remova apenas:
- comandos
- vocativos
- conectivos inúteis

Exemplos:
- Hana
- pai
- filha
- pra mim
- por favor
- toca
- abre
- coloca
- pesquisa
- procura
- ai

━━━━━━━━━━━━━━━━━━━━━━
NÃO REMOVER
━━━━━━━━━━━━━━━━━━━━━━

NUNCA remover:
- nomes de músicas
- nomes de artistas
- temas principais
- assuntos do vídeo
- títulos
- bandas
- pessoas

━━━━━━━━━━━━━━━━━━━━━━
REGRAS CRÍTICAS
━━━━━━━━━━━━━━━━━━━━━━

- NÃO inventar palavras
- NÃO melhorar a query
- NÃO adicionar "youtube"
- NÃO adicionar "tutorial"
- NÃO adicionar "video"
- NÃO adicionar "música"

A query deve conter SOMENTE o conteúdo principal do pedido.

━━━━━━━━━━━━━━━━━━━━━━
EXEMPLOS
━━━━━━━━━━━━━━━━━━━━━━

Input:
"Hana, toca rule da ado para mim"

Output:
rule ado

---

Input:
"coloca headbanger do babymetal"

Output:
headbanger babymetal

---

Input:
"Hana, abre a música Gênio Delicado do Rafão Music pro pai"

Output:
gênio delicado rafão music

---

Input:
"abre algum vídeo sobre o caso do Ganley ai"

Output:
caso Ganley

---

Input:
"toca bring me to life do evanescence"

Output:
bring me to life evanescence

---

Input:
"abre vídeo do ronnie coleman treinando"

Output:
ronnie coleman treinando

━━━━━━━━━━━━━━━━━━━━━━
REGRA FINAL
━━━━━━━━━━━━━━━━━━━━━━

- retornar SOMENTE a query
- nenhuma explicação
- nenhuma frase
- nenhum JSON
"""
}
    messages = [
        system_open_youtube,
        {
            "role": "user",
            "content": Pai
        }
    ]
    query = requests.post("http://127.0.0.1:11434/api/chat",
        json={
            "model": "qwen2.5:3b",
            "messages": messages,
            "stream": False
        }
    )
    query = json.loads(query.text)
    query = query['message']['content']
    ydl_opts = {
    "default_search": "ytsearch1",
    "skip_download": True,
    "quiet": True,
    "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"{query}", download=False)

        primeiro_video = info["entries"][0]
        link_completo = primeiro_video["webpage_url"]

    return query, link_completo














def TOOLS_log(title: str, lines: dict, width: int = 60):
    inner = width - 2

    def wrap_line(text):
        return textwrap.wrap(str(text), width=inner)

    def print_line(text):
        print("║" + text.ljust(inner) + "║")

    def print_wrapped(label, value):
        wrapped = wrap_line(f"{label} → {value}")

        for i, line in enumerate(wrapped):
            if i == 0:
                print_line(line)
            else:
                print_line("  " + line)

    print("╔" + "═" * width + "╗")
    print("║" + "🧩 TOOLS EXECUTION".center(inner) + "║")
    print("╠" + "═" * width + "╣")

    print_line(f"TOOL → {title}")

    print("╠" + "═" * width + "╣")

    for k, v in lines.items():
        print_wrapped(k.upper(), v)

    print("╚" + "═" * width + "╝")