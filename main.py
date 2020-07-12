import requests
from bs4 import BeautifulSoup
import re
from telegram.ext import Updater, CommandHandler
import json
updater = Updater(token='1323800166:AAHC06rNXnQgKPJoCZqpoS8Z0eSOOga6fOs', use_context=True)

dispatcher = updater.dispatcher

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
})

welcome_text = "Что бы получить magnet-ссылку, наберите /magnet *ссылка на тему рутрекера*\nНапример: /magnet https://rutracker.org/forum/viewtopic.php?t=1149720"


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)


def magnet(update, context):
    url = context.args[0]
    html_text = load_html(url, s)
    magnet_link = get_link(html_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Magnet link: `{}`".format(magnet_link), parse_mode='MarkDown')


def register(update, context):
    credentials = context.args
    user_id = update.message.from_user['id']
    users = {user_id: {"address": credentials[0], "port": credentials[1], "username": credentials[2], "password": credentials[3]}}
    with open('data.json', 'r+') as file:
        data = json.load(file)
        temp = data['Users']
        temp.append(users)

    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

    context.bot.send_message(chat_id=update.effective_chat.id, text="Вы добавили сервер {0}:{1}, ваш id - {2}".format(credentials[0], credentials[1], user_id))


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

magnet_handler = CommandHandler('magnet', magnet)
dispatcher.add_handler(magnet_handler)

register_handler = CommandHandler('register', register)
dispatcher.add_handler(register_handler)

updater.start_polling()


def load_html(url, session):
    request = session.get(url)
    return request.text


def get_link(text):
    soup = BeautifulSoup(text, 'html.parser')
    magnet_link = soup.find('a', {'class': 'magnet-link'})
    match = re.search(r'href=[\'"]?([^\'" >]+)', str(magnet_link))
    return match.group(1)
