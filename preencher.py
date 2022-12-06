# selenium 4
import array
import json
import time
from datetime import datetime, timedelta

import pandas as pd
from IPython.display import display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

config = json.load(open('config.json'))

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)


def abrirJiraLoga():
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), chrome_options=chrome_options)
    url = config['url'] + "/login.jsp?permissionViolation=true&os_destination=%2Fsecure%2FTempo.jspa&page_caps=&user_role=#/my-work/timesheet"
    driver.get(url)
    # logar
    driver.find_element(
        by=By.XPATH, value='//*[@id="login-form-username"]').send_keys(config['user'])
    driver.find_element(
        by=By.XPATH, value='//*[@id="login-form-password"]').send_keys(config['password'])
    driver.find_element(
        by=By.XPATH, value='//*[@id="login-form-submit"]').click()
    abrirRegistro(driver)


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

    dif = t2-t1
    time = dif.total_seconds()

    if value.get('time'):
        time += value.get('time')

    if t1.hour < 12 and t2.hour > 13:
        time -= 3600

    return {
        **value, 'time': time,  'str_hora': str_hora, 'str_date': str_date, 'created': created}


def abrirExcel():
    newTabela = []
    newTabelaFaltante = []
    tabela = pd.read_excel('jira.xlsx')
    for i, issue in enumerate(tabela["Issue"]):
        created = tabela.loc[i, "Created"]
        str_date = created.strftime("%d/%b/%Y")
        str_hora = created.strftime("%H:%M:%S")
        if checkIssue(newTabela, issue):
            ultimoI = 0
            for i in range(len(newTabela)):
                value = newTabela[i]
                if issue == value.get('issue'):
                    ultimoI = i

            value = newTabela[ultimoI]

            if value.get('str_date') == str_date:
                newTabela[ultimoI] = dataIgual(
                    value, str_hora, str_date, created)
            else:
                t1 = datetime.strptime(
                    value.get('str_date'), "%d/%b/%Y")
                t2 = datetime.strptime(str_date, "%d/%b/%Y")
                diffData = abs((t2-t1).days)
                if (diffData == 1):
                    newTabela[ultimoI] = dataIgual(
                        value, '18:00:00', value.get('str_date'), str_date + ' 18:00:00')
                    append = dataIgual({
                        'created': created,
                        'str_date': str_date,
                        'issue': issue,
                        'str_hora': '08:00:00',
                        'time': 0.0
                    }, str_hora, str_date, created)
                    newTabela.append(append)
                else:
                    dateIni = datetime.strptime(
                        value.get('str_date'), "%d/%b/%Y")
                    dateFim = datetime.strptime(str_date, "%d/%b/%Y")
                    for sum in range(min(diffData, 5)):
                        dt = dateIni + timedelta(days=sum)
                        if dt.strftime("%d/%b/%Y") == dateIni.strftime("%d/%b/%Y"):
                            newTabela[ultimoI] = dataIgual(
                                value, '18:00:00', value.get('str_date'), str_date + ' 18:00:00')
                        elif dt.strftime("%d/%b/%Y") == dateFim.strftime("%d/%b/%Y"):
                            append = dataIgual({
                                'created': created,
                                'str_date': str_date,
                                'issue': issue,
                                'str_hora': '08:00:00',
                                'time': 0.0
                            }, str_hora, str_date, created)
                            newTabela.append(append)
                        else:
                            append = dataIgual({
                                'created': dt.strftime("%d/%b/%Y") + " 12:00:00",
                                'str_date': dt.strftime("%d/%b/%Y"),
                                'issue': issue,
                                'str_hora': '08:00:00',
                                'time': 0.0
                            }, "12:00:00", dt.strftime("%d/%b/%Y"), dt.strftime("%d/%b/%Y") + " 12:00:00")
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
    return subtrairHora(soma, separarPorData(soma))
# abrir registro


def abrirRegistro(driver):

    # driver.find_element(by=By.XPATH, value='//*[@id="logAnother"]').click()
    demanda = abrirExcel()
    for i in range(len(demanda)):
        driver.find_element(
            by=By.XPATH, value='//*[@id="tempo-nav"]/div[2]/div/div[2]/div[3]/span[3]/button').click()
        value = demanda[i]
        hours = "%dh %dm" % hm_from_seconds(value.get('time'))
        preencher(driver, value.get('issue'), hours,
                  formataDataJira(value.get('str_date')))
    driver.close()


def preencher(driver, demanda, hora, data):
    print({'data': data, 'demanda': demanda}, end='\n')
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

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="tempo-nav"]/div[2]/div/div[3]/div[1]/div[3]/div/div/div[2]/footer/div[2]/button[1]'))).click()


def separarPorData(newTabela):
    countHora = []
    for i in range(len(newTabela)):
        value = newTabela[i]
        time = value.get('time')
        if time <= 1800:
            time = 1800
        data = value.get('str_date')
        cont = time
        # hours = "%dh %dm" % hm_from_seconds(cont)
        # print({'issue': value.get('issue'), 'str_date': value.get(
        #     'str_date'), 'hours': hours}, end='\n')

        if checkStrDate(countHora, data):
            for i in range(len(countHora)):
                value2 = countHora[i]
                if value2.get('str_date') == data:
                    cont += value2.get('time')
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
        if time < 14400:
            if checkStrDate(newTabelaFaltante, value.get('str_date')):
                for i in range(len(newTabelaFaltante)):
                    valueFaltante = newTabelaFaltante[i]
                    if valueFaltante.get('str_date') == value.get('str_date'):
                        newTabela.append(valueFaltante)
                        time += valueFaltante.get('time')
                        if time > 14400:
                            break
    return newTabela


def subtrairHora(newTabela, countHora):
    for i in range(len(countHora)):
        value = countHora[i]
        time = value.get('time')
        while time > 36000:
            if checkStrDate(newTabela, value.get('str_date')):
                for i in range(len(newTabela)):
                    valueSobra = newTabela[i]
                    if valueSobra.get('str_date') == value.get('str_date'):
                        timeSub = int(valueSobra.get('time')/2)
                        newTabela[i] = {**valueSobra, 'time': timeSub}
                        time -= (valueSobra.get('time')-timeSub)
                        if time < 36000:
                            break

    return newTabela


def printHora(arr):
    for i in range(len(arr)):
        value = arr[i]
        # if value.get('time') > 14400:
        hours = "%dh %dm" % hm_from_seconds(value.get('time'))
        print({**value, 'hours': hours}, end='\n')


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
    days, hours = divmod(hours, 24)
    return (hours, minutes)

    # driver.close()


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


abrirJiraLoga()
