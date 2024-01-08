import json

from jiraone import LOGIN, PROJECT, USER, endpoint, file_reader
from jiraone.module import time_in_status

LOGIN.api = False
config = json.load(open('config.json'))
LOGIN(**{
    "user": config['user'],
    "password": config['password'],
    "url": config['url'],
}
)

# count_start_at = 0
# validate = LOGIN.get(endpoint.myself())
# print(validate)
# extract = LOGIN.get(endpoint.search_users(count_start_at))
# print(endpoint.search_users(count_start_at))
# print(extract)

# key = ["COM-12", "COM-14"]
# key = "COM-12"  # as a string
# key = "COM-12,COM-14" # a string separated by comma
# key = 10034 # an integer denoting the issueid
# key = ["COM-12", "COM-114", "TPS-14", 10024] # a list of issue keys or issue ids
# # a dict using JQL
# name = config['user']
# key = {
#     "jql": 'updated >= 2022-01-01 AND updated <= 2022-12-31 AND author in ("'+name+'") ORDER BY updated DESC'}

print("".center(50, "_"))
print(" Buscar as demandas ".center(50, "-") + "\n")
evolutiva = input("\n Qual Evolutiva? (1, 2, 3) =>")
dataInicial = input("\n Data Inicial? (Y-M-D 2023-01-01) =>")
dataFinal = input("\n Data Final? (Y-M-D 2023-12-31) =>")

key = {
    "jql": f'"Equipe de atendimento" = "Evolutiva {evolutiva}" AND created >= {dataInicial} AND created <= {dataFinal} ORDER BY created DESC, updated DESC'}

if (__name__ == "__main__"):
    status = time_in_status(PROJECT, key, file_reader, pprint=True, is_printable=False,
                            output_format="csv", report_folder="STATUSPAGE",
                            login=LOGIN)
    print(status)
