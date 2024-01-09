# Jira

## Pré-requisitos

Instale usando `pip`. Você precisa estar em python >= 3.6.x para utilizar este script.

- Baixe o python e instale no seu dispositivo visitando [python.org](https://python.org/downloads)

## Instalação

1. Clone o repositório

   ```sh
   git clone https://github.com/LFC94/PreencherJira.git
   ```

2. Instale as dependências do pacote em requirements.txt executando o pip 

   ```sh
    pip install -r requirements.txt
   ```

3. RENOMEAR config.example.json para config.json

4. PREENCHA com os dados do Jira **username** e **password** e **url** em config.json

5. No config.json pode adicionar os periodos que nao devera ser lancado como ferias, feriado local, ou periodo do anos nao desejado.


6. Para gerar a lista de demandas, execute

   ```sh
   python time_status.py
   ```

7. Copie a lista gerada (\STATUSPAGE\time_status.csv) para a raiz do projeto com o nome jira.xlsx

8. Para preencher os dados de hora no jira executável

   ```sh
   python preencher.py
   ```
