
import preencher
from time_status import buscarDemanda
from uteis import menuTelas


def menu():
    MENU = {
        '1': {'title': 'Buscar Demanda', 'function': buscarDemanda},
        '2': {'title': 'Gerar Dados', 'function': preencher.inicio},
    }

    menuTelas(MENU)


if __name__ == "__main__":
    menu()
