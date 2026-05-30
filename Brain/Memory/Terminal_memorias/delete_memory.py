import sqlite3
from .get_memoria import Get_terminal, Get_memoria

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

    return input("➜  ")

def Delete_terminal():
    Get_terminal()
    
    id = int(input_box("Digite o ID da memoria: "))
    memoria_deletada = Get_memoria(id)
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    cursor.execute("""DELETE FROM memorias WHERE ID = ?""", (id, ))
    con.commit()
    con.close()
    
    caixa("Memória deletada", f"{memoria_deletada}")
    input("Clique enter...  ")