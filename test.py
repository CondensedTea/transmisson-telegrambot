import json

credentials = ("google.com", "22", "usr", "pswd")

users = {24: {"address": credentials[0], "port": credentials[1], "username": credentials[2], "password": credentials[3]}}

transremote_user = 'test'
transremote_password = 'test2'

with open('data.json', 'r') as file:
    data = json.load(file)
    print(data)
    for user_list in data['Users']:
        for item_in_list in user_list:
            for user_id, id_values in item_in_list:
                for value_name, value_value in id_values:
                    if user_id == 24:
                        transremote_user = value_value['username']
                        transremote_password = value_value['password']

print(transremote_user, transremote_password)
