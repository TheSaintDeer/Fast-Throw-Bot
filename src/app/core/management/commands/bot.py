import requests
import re

import telebot
from telebot.types import Message
from django.conf import settings
from django.core.management.base import BaseCommand

import core.management.commands.messages as m

base_url = 'http://127.0.0.1:8000/api/'
bot = telebot.TeleBot(settings.API_KEY)

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, m.start_answer)

@bot.message_handler(commands=['tables'])
def show_tables(message: Message):
    r = requests.get(base_url+'table/')
    bot.send_message(message.chat.id, m.send_all_tables(r.json()))

@bot.message_handler(regexp='^\/roll .{1,20}$')   
def roll_dice(message: Message):
    table = message.text[6:]
    r = requests.get(base_url+'table/roll/', data={
        'name': table
    })
    entry = r.json()['entry']
    bot.send_message(message.chat.id, entry)

@bot.message_handler(regexp='^\/show .{1,20}$')
def show_entries(message: Message):
    table = message.text[6:]
    r = requests.get(base_url+'table/full/', data={
        'name': table
    })
    bot.send_message(message.chat.id, r.json()['url'])

@bot.message_handler(regexp='^\/search .{1,20}$')
def show_all_tags(message: Message):
    pass #search by keyword


class Command(BaseCommand):
    help = "Run the bot"
    
    def handle(self, *args, **options):
        bot.polling()