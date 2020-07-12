import json

credentials = ("google.com", "22", "usr", "pswd")

users = {24: {"address": credentials[0], "port": credentials[1], "username": credentials[2], "password": credentials[3]}}
with open('data.json', 'r+') as file:
    data = json.load(file)
    temp = data['Users']
    # print(data)
    temp.append(users)

with open('data.json', 'w') as file:
    json.dump(data, file, indent=4)
