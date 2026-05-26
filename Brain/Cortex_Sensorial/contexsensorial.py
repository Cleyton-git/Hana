from ..Ears.ouvidos import Fala_Pai
import textwrap

LARGURA = 54


def Cortex_sensorial(TERMINAL_MODE, interacao):
    """
        Responsavel por receber o input do usuario por teclado e voz
    """
    if TERMINAL_MODE:
        Pai = input("PAI -> ")
        print("╔" + "═" * (LARGURA + 2) + "╗")
        linha(f"{f'HANA | INTERAÇÃO #{interacao}':^{LARGURA}}")
        print("╠" + "═" * (LARGURA + 2) + "╣")
        linha(f"PAI | {Pai}")
        
        return Pai
    else:
        print("╔" + "═" * (LARGURA + 2) + "╗")
        linha(f"{f'HANA | INTERAÇÃO #{interacao}':^{LARGURA}}")
        print("╠" + "═" * (LARGURA + 2) + "╣")
        Pai = Fala_Pai()
        return Pai

def linha(texto):
    linhas = textwrap.wrap(
        str(texto),
        width=LARGURA
    )
    for l in linhas:
        print(f"║ {l:<{LARGURA}} ║")
