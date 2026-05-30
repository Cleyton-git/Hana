import sqlite3

LARGURA = 80

def Get_terminal():
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()

    cursor.execute(f"SELECT * FROM memorias ORDER BY id ASC")
    rows = cursor.fetchall()

    print("╔" + "═" * LARGURA + "╗")
    print(f"║{'MEMÓRIAS DA HANA'.center(LARGURA)}║")
    print("╠" + "═" * LARGURA + "╣")

    for memoria in rows:
        texto = f"[{memoria[0]}] {memoria[1]}, {memoria[2]}, {memoria[5]}"

        while len(texto) > LARGURA:
            print(f"║{texto[:LARGURA]}║")
            texto = texto[LARGURA:]

        print(f"║{texto.ljust(LARGURA)}║")

    print("╚" + "═" * LARGURA + "╝")

    con.close()
    input("Clique enter...  ")

def Get_memoria(id_memoria):
    con = sqlite3.connect("Brain/BD/hana_memorys.db")
    cursor = con.cursor()
    memoria = cursor.execute("""SELECT memory FROM memorias WHERE ID = ?""", (id_memoria, )).fetchone()
    con.close()
    
    if memoria:
        return memoria[0]
    
    return "Memoria não encontrada"
    
