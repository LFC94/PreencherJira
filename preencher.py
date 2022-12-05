# selenium 4
import array
import json
import time
from datetime import datetime

import pandas as pd
from IPython.display import display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

config = json.load(open('config.json'))

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)


def abrirJiraLoga():
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), chrome_options=chrome_options)
    driver.get("https://jira.unyleya.com.br/login.jsp?permissionViolation=true&os_destination=%2Fsecure%2FTempo.jspa&page_caps=&user_role=#/    my-work/timesheet")
    # logar
    driver.find_element(
        by=By.XPATH, value='//*[@id="login-form-username"]').send_keys(config['user'])
    driver.find_element(
        by=By.XPATH, value='//*[@id="login-form-password"]').send_keys(config['password'])
    driver.find_element(
        by=By.XPATH, value='//*[@id="login-form-submit"]').click()
    abrirRegistro(driver)


def abrirExcel():
    newTabela = []
    tabela = pd.read_excel('jira1.xlsx')
    for i, linha in enumerate(tabela["linha"]):
        created = tabela.loc[i, "Created"]
        issue = tabela.loc[i, "Issue"]
        str_date = created.strftime("%d/%b/%Y")
        str_hora = created.strftime("%H:%M:%S")
        if checkKey(newTabela, issue, str_date):
            for i in range(len(newTabela)):
                value = newTabela[i]
                if issue == value.get('issue') and value.get('str_date') == str_date:
                    t1 = datetime.strptime(value.get('str_hora'), "%H:%M:%S")
                    t2 = datetime.strptime(str_hora, "%H:%M:%S")
                    dif = t2-t1
                    time = dif.total_seconds()
                    if value.get('time'):
                        time += value.get('time')

                    newTabela[i] = {**value, 'time': time}
        else:
            newTabela.append({
                'created': created,
                'str_date': str_date,
                'issue': issue,
                'str_hora': str_hora,
                'time': 0.0
            })
    
    
    countHora = []
    for i in range(len(newTabela)):
        value = newTabela[i]
        time = value.get('time')
        if time <= 1800:
            time = 1800
        data = value.get('str_date')
        cont = time

        def checkKey2(arr, str_date):
            if len(arr) < 1:
                return False
            for dic in arr:
                if dic.get('str_date') == str_date:
                    return True
            return False
        if checkKey2(countHora, data):
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

        # hours = "%dh %dm" % hm_from_seconds(time)
        # newTabela[i] = {**value, 'time2': time, 'hours': hours}
        # print(newTabela[i], end='\n')
    for i in range(len(countHora)):
        value = countHora[i]
        hours = "%dh %dm" % hm_from_seconds(value.get('time'))
        print({'str_date': value.get('str_date'), 'hours': hours}, end='\n')
# abrir registro


def abrirRegistro(driver):
    driver.find_element(
        by=By.XPATH, value='//*[@id="tempo-nav"]/div[2]/div/div[2]/div[3]/span[3]/button').click()
    driver.find_element(by=By.XPATH, value='//*[@id="logAnother"]').click()


def preencher(driver, demanda, time, data):
    inputDemanda = driver.find_element(
        by=By.XPATH, value='//*[@id="issuePickerInput"]')
    inputDemanda.send_keys(demanda)
    time.sleep(5)
    inputDemanda.send_keys(Keys.ENTER)
    inputTime = driver.find_element(
        by=By.XPATH, value='//*[@id="timeSpentSeconds"]')
    inputTime.send_keys(time)
    inputData = driver.find_element(
        by=By.XPATH, value='//*[@id="started"]')
    i = 1
    campo = ''
    while i < 12:
        inputData.send_keys(Keys.BACKSPACE)
        i += 1
    inputData.send_keys(campo + data)
    driver.find_element(
        by=By.XPATH, value='//*[@id="tempo-nav"]/div[2]/div/div[3]/div[1]/div[3]/div/div/div[2]/footer/div[2]/button[1]').click()


def checkKey(arr, issue, str_date):
    if len(arr) < 1:
        return False
    for dic in arr:
        if dic.get('issue') == issue and dic.get('str_date') == str_date:
            return True
    return False


def hm_from_seconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return (hours, minutes)


    # driver.close()
abrirExcel()
