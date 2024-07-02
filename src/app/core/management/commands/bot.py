import requests
import re

import telebot
from telebot.types import Message
from django.conf import settings
from django.core.management.base import BaseCommand

base_url = 'http://127.0.0.1:8000/api/'
bot = telebot.TeleBot(settings.API_KEY)

start_answer = '''
View all tables: /tables
Roll the dice on one of them: /roll {Table}
Show entire table: /show {Table}
Search tables by keyword: /search {Keyword}
'''

def send_all_tables(json_list):
    text = ''
    for jl in json_list:
        text += f"{jl['name']}. {jl['desc']}\n\n"
    return text

def send_request(msg: Message, url, data=None):
    try:
        return requests.get(url, data=data)
    except:
        bot.send_message(msg.chat.id, 'Something has gone wrong.')
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, start_answer)

@bot.message_handler(commands=['tables'])
def show_tables(message: Message):
    r = send_request(message, base_url+'table/')
    if r.status_code == 200:
        bot.send_message(message.chat.id, send_all_tables(r.json()))
    else:
        bot.send_message(message.chat.id, 'Something has gone wrong.')

@bot.message_handler(regexp='^\/roll .{1,20}$')   
def roll_dice(message: Message):
    table = message.text[6:]
    r = send_request(message, base_url+'table/roll/', data={
        'name': table
    })
    if r.status_code == 200:
        bot.send_message(message.chat.id, r.json()['entry'])
    else:
        bot.send_message(message.chat.id, f'You may have entered the table name incorrectly. Did you mean to introduce "{table}"?')

@bot.message_handler(regexp='^\/show .{1,20}$')
def show_entries(message: Message):
    table = message.text[6:]
    r = send_request(message, base_url+'table/full/', data={
        'name': table
    })
    if r.status_code == 200:
        bot.send_message(message.chat.id, r.json()['url'])
    else:
        bot.send_message(message.chat.id, f'You may have entered the table name incorrectly. Did you mean to introduce "{table}"?')

@bot.message_handler(regexp='^\/search .{1,20}$')
def search_by_keyword(message: Message):
    keyword = message.text[8:]
    r = send_request(message, base_url+'table/search/', data={
        'keyword': keyword
    })
    if r.status_code == 200:
        bot.send_message(message.chat.id, send_all_tables(r.json()))
    else:
        bot.send_message(message.chat.id, f'Any not found.')


class Command(BaseCommand):
    help = "Run the bot"
    
    def handle(self, *args, **options):
        bot.polling()