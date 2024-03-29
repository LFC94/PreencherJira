# selenium 4
import array
import json
import os.path
import random
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from IPython.display import display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

config = json.load(open('config.json'))
anoLancamento = 2023


def lancarHorasFaltante():
    abrirJiraLoga(faltante=True)


def lancarHorasDaily():
    abrirJiraLoga(faltante=True, daily=True)


def abrirJiraLoga(faltante=False, daily=False):
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))

    url = config['url'] + "/login.jsp?permissionViolation=true&os_destination=%2Fsecure%2FTempo.jspa&page_caps=&user_role=#/my-work/timesheet"
    driver.get(url)
    # logar
    driver.find_element(
        by=By.XPATH, value='//*[@id="login-form-username"]').send_keys(config['user'])
    driver.find_element(
        by=By.XPATH, value='//*[@id="login-form-password"]').send_keys(config['password'])
    driver.find_element(
        by=By.XPATH, value='//*[@id="login-form-submit"]').click()
    abrirRegistro(driver, faltante=faltante, daily=daily)


def dataIgual(value, str_hora, str_date, created):
    t1 = datetime.strptime(
        value.get('str_hora'), "%H:%M:%S")
    t2 = datetime.strptime(str_hora, "%H:%M:%S")

    if t2.hour > 18:
        t1 = datetime.strptime('18:00:00', "%H:%M:%S")

    if t1 > t2:
        t3 = t1
        t1 = t2
        t2 = t3

    dif = (t2.hour-t1.hour) * 60
    dif += t2.minute-t1.minute
    time2 = dif * 60
    time = time2 + int(value.get('time'))
    return {
        **value, 'time': time, 'time1': time, 'time0': value.get('time'), 'time2': time2,  'str_hora': str_hora, 'str_date': str_date,  'created': created}


def abrirExcel():
    newTabela = []
    newTabelaFaltante = []
    tabela = pd.read_excel('jira.xlsx')
    for i, issue in enumerate(tabela["Issue Key"]):
        created = tabela.loc[i, "Created"]
        created = pd.Timestamp(created).to_pydatetime()
        str_date = created.strftime("%d/%b/%Y")
        str_hora = created.strftime("%H:%M:%S")
        if checkIssue(newTabela, issue):
            ultimoI = -1
            for index in range(len(newTabela)):
                value = newTabela[index]
                if issue == value.get('issue'):
                    ultimoI = index
            if ultimoI < 0:
                continue

            value = newTabela[ultimoI]

            if value.get('str_date') == str_date:
                newTabela[ultimoI] = dataIgual(
                    value, str_hora, str_date, created)
            else:
                dateIni = datetime.strptime(
                    value.get('str_date'), "%d/%b/%Y")
                dateFim = datetime.strptime(str_date, "%d/%b/%Y")
                diffData = abs((dateFim-dateIni).days)
                if (diffData == 0):
                    createdFim = datetime.strptime(
                        str_date + ' 18:00:00', "%d/%b/%Y %H:%M:%S")
                    newTabela[ultimoI] = dataIgual(
                        value, '18:00:00', value.get('str_date'), createdFim)
                    append = dataIgual({
                        'created': created,
                        'str_date': str_date,
                        'issue': issue,
                        'str_hora': '08:00:00',
                        'time': 0.0
                    }, str_hora, str_date, created)
                    newTabela.append(append)
                else:
                    for sum in range(diffData+1):
                        dt = dateIni + timedelta(days=sum)
                        min = random.uniform(50, 59)
                        hor = random.uniform(15, 17)
                        hora = "%d:%d:00" % (hor, min)
                        if dt.strftime("%d/%b/%Y") == dateIni.strftime("%d/%b/%Y"):
                            createdFim = datetime.strptime(dt.strftime(
                                "%d/%b/%Y") + " " + hora, "%d/%b/%Y %H:%M:%S")

                            newTabela[ultimoI] = dataIgual(
                                value, hora, value.get('str_date'), createdFim)
                        elif dt.strftime("%d/%b/%Y") == dateFim.strftime("%d/%b/%Y"):
                            append = dataIgual({
                                'created': dt,
                                'str_date': str_date,
                                'issue': issue,
                                'str_hora': '08:00:00',
                                'time': 0.0
                            }, str_hora, str_date, created)
                            newTabela.append(append)
                        else:
                            createdFim = datetime.strptime(dt.strftime(
                                "%d/%b/%Y") + " " + hora, "%d/%b/%Y %H:%M:%S")
                            append = dataIgual({
                                'created': dt,
                                'str_date': dt.strftime("%d/%b/%Y"),
                                'issue': issue,
                                'str_hora': '08:00:00',
                                'time': 0.0
                            }, hora, dt.strftime("%d/%b/%Y"), createdFim)
                            newTabelaFaltante.append(append)

        else:
            newTabela.append({
                'created': created,
                'str_date': str_date,
                'issue': issue,
                'str_hora': str_hora,
                'time': 900
            })

    countHora = separarPorData(newTabela)
    soma = somarFaltante(newTabela, countHora, newTabelaFaltante)
    subtrair = subtrairHora(newTabela, separarPorData(newTabela))
    return filtraFeriasTimeZerado(subtrair)
# abrir registro


def abrirExcelLancado():
    arr = []
    path_to_file = 'lancado.xlsx'
    if os.path.exists(path_to_file):
        tabela = pd.read_excel(path_to_file)
        for i, issue in enumerate(tabela["Questão-chave"]):
            created = tabela.loc[i, "data de Trabalho"]
            str_date = created.strftime("%d/%b/%Y")
            hora = float("{:.2f}".format(tabela.loc[i, "Horas"]))
            time = hora * 60 * 60
            arr.append({
                'str_date': str_date,
                'time': int(time),
                'hora': hora,
                'issue': issue
            })

    return arr


def abrirRegistro(driver, faltante=False, daily=False):

    # driver.find_element(by=By.XPATH, value='//*[@id="logAnother"]').click()
    if faltante:
        demanda = verificarDiasFaltante(daily=daily)
    else:
        demanda = abrirExcel()

    for i in range(len(demanda)):
        value = demanda[i]
        hours = "%dh %dm" % hm_from_seconds(value.get('time'))
        preencher(driver, value.get('issue'), hours,
                  formataDataJira(value.get('str_date')))
    driver.close()


def preencher(driver, demanda, hora, data):
    print({'data': data, 'demanda': demanda}, end='\n')
    time.sleep(2)
    driver.find_element(
        by=By.XPATH, value='//*[@id="tempo-nav"]/div[2]/div/div[2]/div[3]/span[3]/button').click()
    inputDemanda = driver.find_element(
        by=By.XPATH, value='//*[@id="issuePickerInput"]')
    inputDemanda.send_keys(demanda)
    time.sleep(2)
    inputDemanda.send_keys(Keys.ENTER)
    inputTime = driver.find_element(
        by=By.XPATH, value='//*[@id="timeSpentSeconds"]')
    inputTime.send_keys(hora)
    inputData = driver.find_element(
        by=By.XPATH, value='//*[@id="started"]')
    i = 1
    campo = ''
    while i < 12:
        inputData.send_keys(Keys.BACKSPACE)
        i += 1
    inputData.send_keys(campo + data)

    time.sleep(2)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="tempo-nav"]/div[2]/div/div[3]/div[1]/div[3]/div/div/div[2]/footer/div[2]/button[1]'))).click()


def separarPorData(newTabela, lancado=True):

    countHora = []
    if (lancado):
        countHora = separarPorData(abrirExcelLancado(), False)

    for i in range(len(newTabela)):
        value = newTabela[i]
        time = value.get('time')
        if time <= 1800:
            time = 1800

        data = value.get('str_date')
        cont = int(time)

        if checkStrDate(countHora, data):
            for i in range(len(countHora)):
                value2 = countHora[i]
                if value2.get('str_date') == data:
                    cont += int(value2.get('time'))
                    countHora[i] = {**value2, 'time': cont}
        else:
            countHora.append({
                'str_date': data,
                'time': cont
            })
    return countHora


def somarFaltante(newTabela, countHora, newTabelaFaltante):
    for i in range(len(countHora)):
        value = countHora[i]
        time = value.get('time')
        if time < 28000:
            if checkStrDate(newTabelaFaltante, value.get('str_date')):
                for i in range(len(newTabelaFaltante)):
                    valueFaltante = newTabelaFaltante[i]
                    if valueFaltante.get('str_date') == value.get('str_date'):
                        time += int(valueFaltante.get('time'))
                        faltante = int(valueFaltante.get('time'))
                        if time > 28000:
                            faltante -= time - 28000
                        if faltante > 0:
                            newTabela.append({**valueFaltante, 'time': time})
                        if time > 28000:
                            break

    for index in range(len(newTabelaFaltante)):
        value = newTabelaFaltante[index]
        if checkStrDate(newTabela, value.get('str_date')) == False:
            newTabela.append(value)

    return newTabela


def subtrairHora(newTabela, countHora):
    reajustar = False
    for i in range(len(countHora)):
        value = countHora[i]
        time = int(value.get('time'))
        # print(value.get('str_date') + "**********************", end='\n')
        while time > 32001:
            timeInicio = time
            # print(time, end='\n')
            if checkStrDate(newTabela, value.get('str_date')):
                for indes in range(len(newTabela)):
                    possui = False
                    valueSobra = newTabela[indes]
                    if valueSobra.get('str_date') == value.get('str_date'):
                        # print({**valueSobra, 'indes': indes}, end='\n')
                        possui = True
                        timeSub = int(valueSobra.get('time')/2)
                        newTabela[indes] = {**valueSobra, 'time': timeSub}
                        time -= (valueSobra.get('time')/2)
                        # print({**newTabela[indes], 'indes': indes}, end='\n')
                        if time < 32100:
                            break
                if timeInicio == time:
                    time = 0
            else:
                time = 0
    if (reajustar):
        return subtrairHora(newTabela, separarPorData(newTabela))

    return newTabela


def printHora(arr, excel=False):
    retorno = []
    for i in range(len(arr)):
        value = arr[i]
        # if value.get('time') > 14400:
        stime = value.get('time')
        hours = "%dh %dm" % hm_from_seconds(stime)
        hours2 = timedelta(seconds=stime)
        linha = {**value, 'hours': hours, 'hours2': str(hours2)}
        print(linha, end='\n')
        retorno.append(linha)

    print("****************************")
    if excel:
        df = pd.DataFrame(retorno).to_excel("printHora.xlsx")
        print(df)
    return retorno


def checkIssue(arr, issue):
    if len(arr) < 1:
        return False
    for dic in arr:
        if dic.get('issue') == issue:
            return True
    return False


def checkStrDate(arr, str_date):
    if len(arr) < 1:
        return False
    for dic in arr:
        if dic.get('str_date') == str_date:
            return True
    return False


def hm_from_seconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    # days, hours = divmod(hours, 24)
    return (hours, minutes)


def formataDataJira(data):
    data = datetime.strptime(data, "%d/%b/%Y")
    dia = data.strftime("%d")
    ano = data.strftime("%Y")
    numMes = data.strftime("%m")
    meses = {
        '01': 'jan',
        '02': 'fev',
        '03': 'mar',
        '04': 'abr',
        '05': 'mai',
        '06': 'jun',
        '07': 'jul',
        '08': 'ago',
        '09': 'set',
        '10': 'out',
        '11': 'nov',
        '12': 'dez'}
    return "%s/%s/%s" % (dia, meses.get(numMes), ano)


def filtraFeriasTimeZerado(arrTabela, filZerado=True):
    arrRetorno = []
    for i in range(len(arrTabela)):
        value = arrTabela[i]
        if verificarPeriodoInativo(value.get('str_date')):
            # print({'d': value.get('str_date'), 'if': 1})
            continue

        weekday = datetime.strptime(
            value.get('str_date'), "%d/%b/%Y").weekday()
        if weekday == 5 or weekday == 6:
            # print({'d': value.get('str_date'), 'if': 2})
            continue

        if int(value.get('time')) < 100 and filZerado:
            # print({**value, 'if': 3})
            continue

        arrRetorno.append(value)

    return arrRetorno


def verificarLancamentoIndevido():

    jalancado = abrirExcelLancado()

    for i in range(len(jalancado)):
        value = jalancado[i]

        if verificarPeriodoInativo(value.get('str_date')):
            print({**value})

        weekday = datetime.strptime(
            value.get('str_date'), "%d/%b/%Y").weekday()
        if weekday == 5 or weekday == 6:
            print({**value})


def verificarPeriodoInativo(str_date):
    global anoLancamento

    periodoInativo = [
        {'start': datetime(2000, 1, 1), 'end': datetime(anoLancamento, 1, 1)},
        {'start': datetime(anoLancamento+1, 1, 1), 'end': datetime(2100, 1, 1)}
    ]

    feriados = [
        {'data': datetime(anoLancamento, 1, 1)},  # Ano Novo
        {'data': datetime(anoLancamento, 4, 7)},  # Sexta-Feira Santa
        {'data': datetime(anoLancamento, 4, 21)},  # Dia de Tiradentes
        {'data': datetime(anoLancamento, 5, 1)},  # Dia do Trabalho
        {'data': datetime(anoLancamento, 6, 8)},  # Corpus Christi
        {'data': datetime(anoLancamento, 9, 7)},  # Independência do Brasil
        {'data': datetime(anoLancamento, 10, 12)},  # Nossa Senhora Aparecida
        {'data': datetime(anoLancamento, 10, 15)},  # Dia do Professor
        {'data': datetime(anoLancamento, 10, 28)},  # Dia do Servidor Público
        {'data': datetime(anoLancamento, 11, 2)},  # Dia de Finados
        {'data': datetime(anoLancamento, 11, 15)},  # Proclamação da República
        {'data': datetime(anoLancamento, 12, 25)},  # Natal
    ]

    if "periodoInativo" in config and len(config['periodoInativo']):
        for inativo in config['periodoInativo']:
            if "fim" in inativo and inativo['fim']:
                periodoInativo.append(
                    {
                        'start':  datetime.strptime(inativo['inicio'], "%d/%m/%Y"),
                        'end': datetime.strptime(inativo['fim'], "%d/%m/%Y"),
                    }
                )
            else:
                feriados.append(
                    {'data':  datetime.strptime(inativo['inicio'], "%d/%m/%Y")})

    created = str_date
    created = datetime.strptime(created, "%d/%b/%Y")
    created = datetime(
        int(created.strftime("%Y")),
        int(created.strftime("%m")),
        int(created.strftime("%d"))
    )
    for index in range(len(periodoInativo)):
        periodo = periodoInativo[index]

        start = periodo.get("start")
        end = periodo.get("end")

        if start.date() <= created.date() <= end.date():
            return True

    for index in range(len(feriados)):
        feriado = feriados[index]

        data = feriado.get("data")

        if data.date() == created.date():
            return True

    return False


def verificarDiasFaltante(daily=False):
    global anoLancamento
    arrLancado = separarPorData(abrirExcelLancado(), False)
    dataFaltando = []
    dateIni = datetime.strptime(f'01/01/{anoLancamento}', "%d/%m/%Y")
    t2 = datetime.strptime(f'30/12/{anoLancamento}', "%d/%m/%Y")
    diffData = abs((dateIni-t2).days)
    for sum in range(diffData):
        dataAt = dateIni + timedelta(days=sum)
        dataAt = dataAt.strftime("%d/%b/%Y")
        if not checkStrDate(arrLancado, dataAt):
            if daily:
                min = random.uniform(10, 20)
                dataFaltando.append(
                    {'str_date': dataAt, 'issue': 'GRA-149',   'time': min * 60})
            else:
                min = random.uniform(50, 59)
                hor = random.uniform(6, 7)

                dataFaltando.append(
                    {'str_date': dataAt, 'issue': 'GRA-71',  'time': ((hor*60)+min)*60})
        else:
            if not daily:
                for index in range(len(arrLancado)):
                    value = arrLancado[index]
                    if value.get('str_date') == dataAt:
                        min = random.uniform(25000, 26500)
                        if value.get('time') < min:
                            time = min-value.get('time')-100
                            dataFaltando.append(
                                {'str_date': dataAt, 'issue': 'GRA-71',  'time': time})
                        break

    return filtraFeriasTimeZerado(dataFaltando)


def getHorasDemandaLancadoData():
    printHora(separarPorData(abrirExcelLancado(), False))


def getHorasDemandaData():
    printHora(separarPorData(abrirExcel(), False))


def getHorasDemanda():
    printHora(abrirExcel(), True)


def getHorasFaltantes():
    printHora(verificarDiasFaltante(), True)


def getHorasFaltantesDaily():
    printHora(verificarDiasFaltante(daily=True), True)


def menu():
    print("".center(50, "_"))
    print(" MENU ".center(50, "-") + "\n")
    MENU = {
        '1': {'title': 'Lancar Horas Daily', 'function': lancarHorasDaily},
        '2': {'title': 'Lancar Horas Faltantes (Demanda)', 'function': abrirJiraLoga},
        '3': {'title': 'Lancar Horas Faltantes (Reuniao)', 'function': lancarHorasFaltante},
        '4': {'title': 'Ver horas demanda lancado por data', 'function': getHorasDemandaLancadoData},
        '5': {'title': 'Ver horas demanda por data', 'function': getHorasDemandaData},
        '6': {'title': 'Ver horas demanda', 'function': getHorasDemanda},
        '7': {'title': 'Ver horas faltante', 'function': getHorasFaltantes},
        '8': {'title': 'Ver horas daily', 'function': getHorasFaltantesDaily},
        's': {'title': 'Sair'}
    }

    for key, item in MENU.items():
        title = item.get('title', '').upper()
        print(f"[{key}] - {title}")
    opcao = input("\n=>")

    if opcao not in MENU.keys():
        print("Operação inválida")

    if opcao in MENU.keys() and MENU[opcao].get('function', False):
        print(MENU.get(opcao).get('title').upper().center(50, "-"))
        MENU[opcao].get('function')()
        print("".center(50, "_"))
        menu()


print("".center(50, "_"))
anoLancamento = int(input("\n Ano lancado (2023)? =>"))
menu()
