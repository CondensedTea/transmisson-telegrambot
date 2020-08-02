import requests
from bs4 import BeautifulSoup
import re
from telegram.ext import Updater, CommandHandler
import json
from tokens import *
from transmission_rpc.client import Client

updater = Updater(token, use_context=True)

dispatcher = updater.dispatcher

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
})

welcome_text = "Что бы получить список комманд, наберите /"
command_list = [("server", "зарегистрировать сервер с transmission-remote \n /register <address> <port> <login> <password>"),
                ("add", "Добавить на сервер торрент по ссылке на тему или по 🧲 magnet-ссылке"),
                ("list_torrents", "Вывести список торрентов и их состояние загрузки"),
                ("magnet", "Сделать из ссылки на тему rutracker.org 🧲 magnet-ссылку")]

data_path: str = "/home/pi/telegram/rutracker-py/data.json"
# data_path = "data.json"


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)
    context.bot.set_my_commands(commands=command_list)


def magnet(update, context):
    url = context.args[0]
    magnet_link = get_link(url, s)
    context.bot.send_message(chat_id=update.effective_chat.id, text="🧲Magnet-ссылка: `{}`".format(magnet_link), parse_mode='MarkDown')


def server(update, context):
    credentials = context.args
    user_id = update.message.from_user['id']
    users = {"address": credentials[0], "port": credentials[1], "username": credentials[2], "password": credentials[3]}
    with open(data_path, 'r') as file:
        data = json.load(file)
        if user_id in [user_id]:  # найс костыль бро !!!
            del data["{}".format(user_id)]
        data[user_id] = users
    with open(data_path, 'w') as file:
        json.dump(data, file, indent=4)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Вы добавили сервер {0}:{1}".format(credentials[0], credentials[1]))


def add(update, context):
    json_data = json_auth(update.message.from_user['id'])
    c = Client(host=json_data[0], port=json_data[1], username=json_data[2], password=json_data[3])
    fulltorrentlist = c.get_torrents()
    if "https://rutracker.org/forum/viewtopic.php?t=" in context.args[0]:
        url = context.args[0]
        magnet_link = get_link(url, s)
    elif "magnet:?" in context.args[0]:
        magnet_link = context.args[0]
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Введеная ссылка не подходит. Введите ссылку на топик на rutracker.org или magnet-ссылку")
        return
    c.add_torrent(magnet_link)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Вы добавили торрент {}".format(fulltorrentlist[-1].name))


def list_torrents(update, context):
    json_data = json_auth(update.message.from_user['id'])
    c = Client(host=json_data[0], port=json_data[1], username=json_data[2], password=json_data[3])
    torrent_name_list = ""
    for torrent in c.get_torrents():
        if torrent.progress == 100.0:
            torrent_progress_tag = "✅"
        else:
            torrent_progress_tag = str(int(torrent.progress))+"%"
        torrent_name_list += torrent_progress_tag+" | "+torrent.name+"\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text="Список торрентов:\n"+torrent_name_list)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

magnet_handler = CommandHandler('magnet', magnet)
dispatcher.add_handler(magnet_handler)

server_handler = CommandHandler('server', server)
dispatcher.add_handler(server_handler)

add_handler = CommandHandler('add', add)
dispatcher.add_handler(add_handler)

list_torrents_handler = CommandHandler('list_torrents', list_torrents)
dispatcher.add_handler(list_torrents_handler)

updater.start_polling()


def get_link(url, session):
    request = session.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    magnet_link = soup.find('a', {'class': 'magnet-link'})
    match = re.search(r'href=[\'"]?([^\'" >]+)', str(magnet_link))
    return match.group(1)


def json_auth(user_id):
    user_id_quotes = '{}'.format(user_id)
    with open('data.json', 'r') as file:
        data = json.load(file)
    transremote_address = data[user_id_quotes]["address"]
    transremote_port = data[user_id_quotes]["port"]
    transremote_username = data[user_id_quotes]["username"]
    transremote_password = data[user_id_quotes]["password"]
    return transremote_address, transremote_port, transremote_username, transremote_password
