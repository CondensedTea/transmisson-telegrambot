import requests
from bs4 import BeautifulSoup
import re
from telegram.ext import Updater, CommandHandler
import json
from tokens import *
import subprocess

updater = Updater(token, use_context=True)

dispatcher = updater.dispatcher

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
})

welcome_text = "Что бы получить список комманд, наберите /"
command_list = ("magnet - сделать из ссылки на тему rutracker.org magnet-ссылку",
                "register - зарегистрировать сервер с transmission-remote. /register <address> <port> <login> <password>",
                "add - добавить на сервер с вашими данными торрент по ссылке на тему rutacker.org")


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)
    context.bot.set_my_commands(commands=command_list)

def magnet(update, context):
    url = context.args[0]
    magnet_link = get_link(url, s)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Magnet link: `{}`".format(magnet_link), parse_mode='MarkDown')


def register(update, context):
    credentials = context.args
    user_id = update.message.from_user['id']
    users = {"address": credentials[0], "port": credentials[1], "username": credentials[2], "password": credentials[3]}
    with open('data.json', 'r') as file:
        data = json.load(file)
        data[user_id] = users
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Вы добавили сервер {0}:{1}".format(credentials[0], credentials[1]))


def add(update, context):
    url = context.args[0]
    user_id_quotes = '{}'.format(update.message.from_user['id'])
    with open('data.json', 'r') as file:
        data = json.load(file)
    transremote_address = data[user_id_quotes]["address"]
    transremote_port = data[user_id_quotes]["port"]
    transremote_username = data[user_id_quotes]["username"]
    transremote_password = data[user_id_quotes]["password"]
    magnet_link = get_link(url, s)
    subprocess.call(['transmission-remote', transremote_address + ':' + transremote_port, '-n', transremote_username + ':' + transremote_password, '-a', magnet_link])


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

magnet_handler = CommandHandler('magnet', magnet)
dispatcher.add_handler(magnet_handler)

register_handler = CommandHandler('register', register)
dispatcher.add_handler(register_handler)

add_handler = CommandHandler('add', add)
dispatcher.add_handler(add_handler)

updater.start_polling()


def get_link(url, session):
    request = session.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    magnet_link = soup.find('a', {'class': 'magnet-link'})
    match = re.search(r'href=[\'"]?([^\'" >]+)', str(magnet_link))
    return match.group(1)
