# Jira

## Prerequisites

Install using `pip`. You have to be on python >= 3.6.x in order to utilize this script.

- Download python and install on your device by visiting [python.org](https://python.org/downloads)

## Installation

1. Clone the repo

   ```sh
   git clone https://github.com/LFC94/PreencherJira.git
   ```

2. Install the package's dependencies in requirements.txt with
   pip by running

   ```sh
    pip install -r requirements.txt
   ```

3. RENAME config.example.json TO config.json

4. FILL in Jira **username** AND **password** AND **url** IN config.json

5. In the time_status.py file there is a KEY variable that must be changed to search for your demands

6. To generate the list of demands, run

   ```sh
   python time_status.py
   ```

7. Copy generated list to project root with name jira.xlsx

8. Para preencher os dados de hora no jira executa

   ```sh
   python preencher.py
   ```
