from .get_memoria import Get_terminal
from .create_memoria import  Create_Terminal
from .update_memoria import Update_Terminal
from .delete_memory import Delete_terminal

LARGURA = 60

def Terminal_memoria():
    while True:
        print("╔" + "═" * LARGURA + "╗")
        print(f"║{'TERMINAL'.center(LARGURA)}║")
        print("╠" + "═" * LARGURA + "╣")

        opcoes = [
        "0 - Listar memórias",
        "1 - Criar memória",
        "2 - Atualizar memória",
        "3 - Deletar memória",
        "4 - Estado emocional",
        "5 - Tarefas",
        "6 - Sair"
    ]

        for opcao in opcoes:
            print(f"║ {opcao.ljust(LARGURA - 1)}║")

        print("╚" + "═" * LARGURA + "╝")

        op = input("➜  ")
        executing = Execute(op)
        if executing == "ok":
            pass
        else:
            print("╔" + "═" * LARGURA + "╗")
            print(f"║{'TERMINAL'.center(LARGURA)}║")
            print("╠" + "═" * LARGURA + "╣")
            print(f"║{'TERMINAL DESATIVADO'.center(LARGURA)}║")
            print("╚" + "═" * LARGURA + "╝")
            break

def Execute(op):
    if op == "0":
        Get_terminal()
        return "ok"
    if op == "1":
        Create_Terminal()
        return "ok"
    if op == "2":
        Update_Terminal()
        return "ok"
    if op == "3":
        Delete_terminal()
        return "ok"
    if op == "6":
        return "break"
    
Terminal_memoria()
