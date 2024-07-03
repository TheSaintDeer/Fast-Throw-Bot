import requests

import telebot
from typing import Dict
from telebot.types import Message
from django.conf import settings
from django.core.management.base import BaseCommand

context: Dict[int, Dict[str, int]] = dict()
base_url = 'http://127.0.0.1:8000/api/'
bot = telebot.TeleBot(settings.API_KEY)

start_answer = '''
Show commands: /help
View all tables: /tables
    Previous page: /prev
    Next page: /next
    Certen page: /page {Page}
Roll the dice on one of them: /roll {Table's ID}
Show entire table: /show {Table's ID}
Search tables by keyword: /search {Keyword}
Add to favorite: /save {Table}
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
    
def get_or_create_context(id):
    global context
    if id not in context:
        context[id] = dict()
        context[id] = {"page": 0}
    return context

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, start_answer)

@bot.message_handler(commands=['prev'])
def prev(message: Message):
    ctx = get_or_create_context(message.chat.id)
    if ctx[message.chat.id]["page"] != 0:
        ctx[message.chat.id]["page"] -= 1
    show_tables(message)

@bot.message_handler(commands=['next'])
def next(message: Message):
    ctx = get_or_create_context(message.chat.id)
    ctx[message.chat.id]["page"] += 1
    show_tables(message)

@bot.message_handler(commands=['page'])
def next(message: Message):
    page = message.text[6:]
    ctx = get_or_create_context(message.chat.id)
    ctx[message.chat.id]["page"] += int(page-1)
    show_tables(message)

@bot.message_handler(commands=['tables'])
def show_tables(message: Message):
    ctx = get_or_create_context(message.chat.id)
    r = send_get_request(
        message.chat.id, 
        base_url+'table/?limit=20&offset='+str(ctx[message.chat.id]["page"]*20)
    )
    if r.status_code == 200:
        bot.send_message(message.chat.id, send_all_tables(r.json()['results'], pagination=True), parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Something has gone wrong.')

@bot.message_handler(commands=['roll'])   
def roll_dice(message: Message):
    pk = message.text[6:]
    r = send_get_request(message.chat.id, base_url+'table/roll/', data={
        'pk': pk
    })
    if r.status_code == 200:
        bot.send_message(message.chat.id, r.json()['entry'])
    else:
        bot.send_message(message.chat.id, f'You may have entered the table name incorrectly. Did you mean to introduce "{pk}"?')

@bot.message_handler(commands=['show'])
def show_entries(message: Message):
    pk = message.text[6:]
    r = send_get_request(message.chat.id, base_url+'table/full/', data={
        'pk': pk
    })
    if r.status_code == 200:
        bot.send_message(message.chat.id, r.json()['url'])
    else:
        bot.send_message(message.chat.id, f'You may have entered the table name incorrectly. Did you mean to introduce "{pk}"?')

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
    table = message.text[5:]
    r = requests.post(
        base_url+'telegram_chat/',
        data={
            'chat_id': message.chat.id,
            'table': table
        }
    )


class Command(BaseCommand):
    help = "Run the bot"
    
    def handle(self, *args, **options):
        bot.polling()