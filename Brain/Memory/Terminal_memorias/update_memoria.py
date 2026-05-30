from .get_memoria import Get_terminal, Get_memoria
import json, requests, sqlite3

LARGURA = 70

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

def input_box(label):
    print("╔" + "═" * 50 + "╗")
    print(f"║ {label.ljust(49)}║")
    print("╚" + "═" * 50 + "╝")

    return input("➜ ")

def Update_Terminal():
    Get_terminal()
    caixa("ATUALIZAR MEMÓRIA", "Selecione a memória que será alterada")
    id = int(input("Digite o ID da memoria que vai ser alterada: "))
    memoria_antiga = Get_memoria(id)
    if memoria_antiga == "Memoria não encontrada":
        caixa("MEMÓRIA SELECIONADA", memoria_antiga)
        return
    caixa("MEMÓRIA SELECIONADA", memoria_antiga)
    new_memory = input_box("NOVA MEMÓRIA")
    new_importance = int(input_box("NOVA IMPORTÂNCIA"))
    new_type = (input_box("NOVO TYPE [factual, emotional, contextual]"))
    new_embeding = requests.post("http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": new_memory
            }
    ).json()['embedding']
    embedding_json = json.dumps(new_embeding)
    
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute("""UPDATE memorias
                   SET memory = ?,
                        importance = COALESCE(?, importance),
                        memory_type = COALESCE(?, memory_type),
                        embedding = COALESCE(?, embedding)
                    WHERE ID = ?
                   """, (new_memory, new_importance, new_type, embedding_json, id))
    con.commit()
    con.close()
    caixa(
        "MEMÓRIA ATUALIZADA",
        f"""
ID:
{id}

NOVA MEMÓRIA:
{new_memory}

IMPORTÂNCIA:
{new_importance}
""".strip()
    )
    input("Clique enter...  ")
    