import requests

import telebot
from typing import Dict
from telebot.types import Message
from django.conf import settings
from django.core.management.base import BaseCommand

context: Dict[int, Dict[str, int]] = dict()
context_creation: Dict[int, Dict[str, str]] = dict()
base_url = 'http://127.0.0.1:8000/api/'
bot = telebot.TeleBot(settings.API_KEY)

start_answer = '''
Show commands: /help\n
TABLE:
    View all tables: /tables
        Previous page: /prev
        Next page: /next
        Certain page: /page {Page}
    Roll the dice on one of them: /roll {Table's ID} {Times(not required)}
    Show entire table: /show {List of Table's ID}
    Search tables by keyword: /search {Keyword}\n
MY FAVORITE:
    Add to your favorite list: /save {List of Table's ID}
    Your list of favorite tables: /favorites
    Delete table from your favorite list: /forget {List of Table's ID}
CUSTOM TABLE:
    Create own table: /create
    Delete your table: /delete {Table's ID}
    Show all your tables: /my_tables
'''

def send_all_tables(json_list, pagination=False):
    text = ''
    for jl in json_list:
        text += f"{jl['pk']}. <b>{jl['name']}</b> - {jl['desc']}\n\n"

    if pagination:
        text += '/prev\t/next'
    return text

def send_get_request(id, url, data=None):
    try:
        return requests.get(url, data=data)
    except:
        bot.send_message(id, 'Something has gone wrong.')
        return False
    
def send_post_request(id, url, data=None):
    try:
        return requests.post(url, data=data)
    except:
        bot.send_message(id, 'Something has gone wrong.')
        return False
    
def get_or_create_context(id, type_list=None):
    global context
    if id not in context or type_list != None:
        context[id] = dict()
        context[id] = {"page": 0, "type": type_list}
    
    return context

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, start_answer)

@bot.message_handler(commands=['prev'])
def prev(message: Message):
    ctx = get_or_create_context(message.chat.id)
    if ctx[message.chat.id]["page"] != 0:
        ctx[message.chat.id]["page"] -= 1

    if ctx[message.chat.id]["type"] == 0:
        show_tables(message)
    elif ctx[message.chat.id]["type"] == 1:
        show_custom_tables(message)

@bot.message_handler(commands=['next'])
def next(message: Message):
    ctx = get_or_create_context(message.chat.id)
    ctx[message.chat.id]["page"] += 1

    if ctx[message.chat.id]["type"] == 0:
        show_tables(message)
    elif ctx[message.chat.id]["type"] == 1:
        show_custom_tables(message)

@bot.message_handler(commands=['page'])
def next(message: Message):
    page = message.text[6:]
    try:
        page = int(page)
    except:
        bot.send_message(message.chat.id, f'You may have entered the table name incorrectly. Did you mean to introduce "{page}"?')
    ctx = get_or_create_context(message.chat.id)
    ctx[message.chat.id]["page"] += int(page-1)
    
    if ctx[message.chat.id]["type"] == 0:
        show_tables(message)
    elif ctx[message.chat.id]["type"] == 1:
        show_custom_tables(message)

@bot.message_handler(commands=['tables'])
def show_tables(message: Message):
    ctx = get_or_create_context(message.chat.id, 0)
    r = send_get_request(
        message.chat.id, 
        base_url+'table/?limit=20&offset='+str(ctx[message.chat.id]["page"]*20)
    )
    if r.status_code == 200:
        bot.send_message(message.chat.id, send_all_tables(r.json()['results'], pagination=True), parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Something has gone wrong.')

@bot.message_handler(commands=['show'])
def show_entries(message: Message):
    pks = message.text[6:].split()
    for pk in pks:
        r = send_get_request(message.chat.id, base_url+f'table/{pk}/show/')
        if r.status_code == 200:
            bot.send_message(message.chat.id, f"[{pk}]: {r.json()['url']}")
        else:
            bot.send_message(message.chat.id, f'You may have entered the table name incorrectly. Did you mean to introduce "{pk}"?')

@bot.message_handler(commands=['roll'])   
def roll(message: Message):
    pk, *count = message.text[6:].split()
    c = [1]
    if count:
        try:
            c = range(int(count[0]))
        except:
            bot.send_message(message.chat.id, f'You may have entered the table name incorrectly. Did you mean to introduce "{count[0]}"?')

    for i in c:
        r = send_get_request(message.chat.id, base_url+f'table/{pk}/roll/')
        if r.status_code == 200:
            bot.send_message(message.chat.id, r.json()['entry'])
        else:
            bot.send_message(message.chat.id, f'You may have entered the table name incorrectly. Did you mean to introduce "{pk}"?')
            return

@bot.message_handler(commands=['search'])
def search_by_keyword(message: Message):
    keyword = message.text[8:]
    r = send_get_request(message.chat.id, base_url+'table/search/', data={
        'keyword': keyword
    })
    if r.status_code == 200:
        bot.send_message(message.chat.id, send_all_tables(r.json()['results'][:20]), parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f'Any not found.')

@bot.message_handler(commands=['save'])
def save_to_favorite(message: Message):
    pks = message.text[6:].split()
    for pk in pks:
        r = send_post_request(
            message.chat.id,
            base_url+'favorite/',
            data={
                'telegramchat': message.chat.id,
                'table': pk
            }
        )
        if r.status_code == 200:
            bot.send_message(message.chat.id, f'Table [{pk}] was added to favorites.')
        elif r.status_code == 500:
            bot.send_message(message.chat.id, f'You may have entered the table name incorrectly. Did you mean to introduce "{pk}"?')
        else:
            bot.send_message(message.chat.id, f'Table [{pk}] has already been saved previously.')

@bot.message_handler(commands=['favorites'])
def favorite_list(message: Message):
    r = send_get_request(message.chat.id, base_url+'telegram_chat/favorites/', 
        data={
            'chat_id': message.chat.id
        }
    )

    if r.status_code == 200:
        bot.send_message(message.chat.id, send_all_tables(r.json()[:20]), parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Something has gone wrong.')

@bot.message_handler(commands=['forget'])
def delete_from_favorite(message: Message):
    pks = message.text[8:].split()
    for pk in pks:
        r = requests.delete(
            base_url+'favorite/delete/',
            data={
                'telegramchat': message.chat.id,
                'table': pk
            }
        )
        if r.status_code == 204:
            bot.send_message(message.chat.id, f'Table [{pk}] was deleted from favorites.')
        else:
            bot.send_message(message.chat.id, f'Table [{pk}] do not include in your favorite list.')

def custom_table(msg: Message):
    global context_creation
    if msg.chat.id not in context_creation:
        context_creation[msg.chat.id] = dict()

    if 'name' in context_creation[msg.chat.id]:
        r = send_post_request(
            msg.chat.id,
            base_url+'table/create_custom_table/',
            data={
                'telegramchat': msg.chat.id,
                'name': context_creation[msg.chat.id]['name'],
                'desc': msg.text
            }
        )
        context_creation[msg.chat.id] = dict()
        bot.send_message(msg.chat.id, f"Enter entry or /end:")
        bot.register_next_step_handler(msg, add_entry, r.json()['pk'])

    elif 'requested' in context_creation[msg.chat.id]:
        context_creation[msg.chat.id]["name"] = msg.text
        bot.send_message(msg.chat.id, f"Enter description of table:")
        bot.register_next_step_handler(msg, custom_table)
    else:
        context_creation[msg.chat.id] = {"requested": "1"}
        bot.send_message(msg.chat.id, f"Enter name of table:")
        bot.register_next_step_handler(msg, custom_table)

def add_entry(msg: Message, pk):
    if msg.text == '/end':
        bot.send_message(msg.chat.id, f"Table [{pk}] was created.")
        return
    
    r = send_post_request(
        msg.chat.id,
        base_url+'entry/',
        data={
            'text': msg.text,
            'table': pk,
        }
    )
    bot.send_message(msg.chat.id, f"Enter entry or /end:")
    bot.register_next_step_handler(msg, add_entry, pk)

@bot.message_handler(commands=['create'])
def add_custom_table(message: Message):
    custom_table(message)

@bot.message_handler(commands=['delete'])
def delete_custom_tables(message: Message):
    pks = message.text[8:].split()
    for pk in pks:
        r = requests.delete(
            base_url+'table/delete_custom_table/',
            data={
                'telegramchat': message.chat.id,
                'table': pk
            }
        )
        if r.status_code == 204:
            bot.send_message(message.chat.id, f'Table [{pk}] was deleted.')
        else:
            bot.send_message(message.chat.id, f'Table [{pk}] does not exist.')

@bot.message_handler(commands=['my_tables'])
def show_custom_tables(message: Message):
    ctx = get_or_create_context(message.chat.id, 1)
    r = send_get_request(
        message.chat.id, 
        base_url+'table/list_custom_tables/?limit=20&offset='+str(ctx[message.chat.id]["page"]*20),
        data={
            'telegramchat': message.chat.id
        }
    )
    if r.status_code == 200:
        bot.send_message(message.chat.id, send_all_tables(r.json()['results'], pagination=True), parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Something has gone wrong.')

class Command(BaseCommand):
    help = "Run the bot"
    
    def handle(self, *args, **options):
        bot.polling()