import requests
import sqlite3
import json

LARGURA = 70

def input_box(label):
    print("╔" + "═" * 50 + "╗")
    print(f"║ {label.ljust(49)}║")
    print("╚" + "═" * 50 + "╝")

    return input("➜  ")

def caixa(titulo, conteudo):
    print("╔" + "═" * LARGURA + "╗")
    print(f"║{titulo.center(LARGURA)}║")
    print("╠" + "═" * LARGURA + "╣")

    linhas = conteudo.split("\n")

    for linha in linhas:
        linha = linha.strip()

        while len(linha) > LARGURA:
            print(f"║{linha[:LARGURA].center(LARGURA)}║")
            linha = linha[LARGURA:]

        print(f"║{linha.center(LARGURA)}║")

    print("╚" + "═" * LARGURA + "╝")

def Create_Terminal():
    memory = input_box("Digite a nova memória")
    importance = int(input_box("Digite a importancia dela"))

    caixa("PROCESSANDO", "Gerando embedding da memória...")

    embedding = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": memory
        }
    ).json()['embedding']

    embedding_json = json.dumps(embedding)

    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute("INSERT INTO memorias (memory, importance, embedding) VALUES(?, ?, ?)", (memory, importance, embedding_json))
    con.commit()
    con.close()

    caixa("MEMÓRIA SALVA",
        f"""

MEMORY:
{memory}

IMPORTANCE:
{importance}
""".strip())
    input("Digite enter...")
