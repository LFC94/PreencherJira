import json
import os
import re

from InquirerPy import inquirer, prompt
from InquirerPy.base.control import Choice


def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True


def menuTelas(MENU={}):
    print("".center(50, "_"))
    print("MENUS".center(50, "-") + "\n")
    MENU['s'] = {'title': 'Sair'}
    choices = []
    for key, item in MENU.items():
        choices.append(Choice(name=item.get('title', '').upper(), value=key))

    opcao = prompt([{
        "type": "rawlist",
        "choices": choices,
        "message": "Selecionar opção desejada:",
    }])[0]

    if opcao not in MENU.keys():
        print(f"{opcao} Operação inválida")

    if opcao in MENU.keys() and MENU[opcao].get('function', False):
        os.system('cls' if os.name == 'nt' else "printf '\033c'")
        print(MENU.get(opcao).get('title').upper().center(50, "-"))
        MENU[opcao].get('function')()
        print("".center(50, "_"))
        menuTelas(MENU)


def printLoading(porcentagem):
    print(f"⌛ {porcentagem}% " + "".center(porcentagem, "▪"), end='\r')


def formatCPF(cpf):
    try:
        cpf = str(int(cpf))
    except ValueError:
        return ''

    if len(cpf) < 11:
        cpf = cpf.zfill(11)
    return '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])


def extract_between(text, start, end='', endForm=''):
    if len(text) > 500:
        text = text[:500]
    # Usando expressão regular para capturar texto entre as duas strings
    pattern = re.compile(re.escape(start) + r'(.*?)' +
                         endForm + re.escape(end))
    # matches = pattern.findall(text)
    match = pattern.search(text)
    return match.group(1) if match else None


def extract_start(text, end):
    try:
        if len(text) > 500:
            text = text[:500]
        # Usando expressão regular para capturar texto entre as duas strings
        pattern = re.compile(r'(.*?)' + re.escape(end))
        # matches = pattern.findall(text)
        match = pattern.search(text)
        return match.group(1).strip() if match else None
    except BufferError as err:
        return None


def confirmacao(message):
    return inquirer.confirm(
        message=message,
        default=True,
        confirm_letter="s",
        reject_letter="n",
        transformer=lambda result: "Sim" if result else "Não",
    ).execute()


def inputText(message):
    return inquirer.text(message=message).execute()


def inputNumber(message):
    return inquirer.number(message=message).execute()
