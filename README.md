# Jira

## Pré-requisitos

Certifique-se de ter o Python instalado em sua máquina com a versão 3.12.x para utilizar este script.

- Faça o download e instale o Python visitando [python.org](https://python.org/downloads).

## Instalação

1. **Instale as dependências do PIPENV usando o pip**

   ```sh
   pip install pipenv
   ```

2. **Clone o repositório**

   ```sh
   git clone https://github.com/LFC94/PreencherJira.git
   ```

3. **Instalar dependencia do projeto**
   Na pasta do projeto.
   ```sh
   pipenv shell
   pipenv sync
   ```

4. **Renomeie o arquivo `config.example.json` para `config.json`**

5. **Preencha o arquivo `config.json` com os dados do Jira, incluindo *username*, *password*, e *url***

6. **No `config.json`, é possível adicionar períodos que não devem ser incluídos, como férias, feriados locais ou períodos indesejados do ano**
   - Ex : Carnaval de 2023 (período) e Aniversario da Cidade (data única)
   ```json
      "periodoInativo": [
          {
            "inicio": "20/02/2023",
            "fim": "22/02/2023"
          },
          {
            "inicio": "20/09/2023"
          }
     ]
   ```

   - Ex : Lançar a partir de Agosto
   ```json
      "periodoInativo": [
          {
            "inicio": "01/01/2023",
            "fim": "31/07/2023"
          }
     ]

7. **Para gerar a lista de demandas, execute**

   ```sh
   pipenv run python init.py
   ```
   Selecionar a opção 1 - Buscar Demanda

8. **Ira porguntar se deseja separa:**

   **Se sim:**
   Copie a lista gerada (localizada em a raiz do projeto com o nome `output.xlsx`) para a raiz do projeto com o nome `jira.xlsx`

   **Se não:**
   Copie a lista gerada (localizada em `\STATUSPAGE\time_status.csv`) para a raiz do projeto com o nome `jira.xlsx`

10. **Para preencher os dados de horas no Jira, execute**

   ```sh
   pipenv run python init.py
   ```
   Selecionar a opção 2 - Gerar Dados
