# Jira

## Pré-requisitos

Certifique-se de ter o Python instalado em sua máquina com a versão igual ou superior a 3.6.x para utilizar este script.

- Faça o download e instale o Python visitando [python.org](https://python.org/downloads).

## Instalação

1. **Clone o repositório**

   ```sh
   git clone https://github.com/LFC94/PreencherJira.git
   ```

2. **Instale as dependências do pacote listadas no arquivo `requirements.txt` usando o pip**

   ```sh
   pip install -r requirements.txt
   ```

3. **Renomeie o arquivo `config.example.json` para `config.json`**

4. **Preencha o arquivo `config.json` com os dados do Jira, incluindo *username*, *password*, e *url***

5. **No `config.json`, é possível adicionar períodos que não devem ser incluídos, como férias, feriados locais ou períodos indesejados do ano**
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

6. **Para gerar a lista de demandas, execute**

   ```sh
   python time_status.py
   ```
7. **Ira porguntar se deseja separa:**

   **Se sim:**
   Copie a lista gerada (localizada em a raiz do projeto com o nome `output.xlsx`) para a raiz do projeto com o nome `jira.xlsx`

   **Se não:**
   Copie a lista gerada (localizada em `\STATUSPAGE\time_status.csv`) para a raiz do projeto com o nome `jira.xlsx`

9. **Para preencher os dados de horas no Jira, execute**

   ```sh
   python preencher.py
   ```
