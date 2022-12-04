import json

from jiraone import LOGIN, PROJECT, USER, endpoint, file_reader
from jiraone.module import time_in_status

LOGIN.api = False
config = json.load(open('config.json'))
LOGIN(**config)

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

key = {
    "jql": '"Equipe de atendimento" = "Evolutiva 1" AND created >= 2022-01-01 AND created <= 2022-12-31 ORDER BY created DESC, updated DESC'}

if (__name__ == "__main__"):
    status = time_in_status(PROJECT, key, file_reader, pprint=True, is_printable=False,
                            output_format="csv", report_folder="STATUSPAGE",
                            login=LOGIN)
    print(status)
