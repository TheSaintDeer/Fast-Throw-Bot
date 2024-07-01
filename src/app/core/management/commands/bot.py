import requests

import telebot
from telebot.types import Message
from django.conf import settings
from django.core.management.base import BaseCommand

import core.management.commands.messages as m


bot = telebot.TeleBot(settings.API_KEY)
base_url = 'http://127.0.0.1:8000/api/'

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, m.start_answer)

@bot.message_handler(commands=['tables'])
def show_tables(message: Message):
    r = requests.get(base_url+'table/')
    bot.send_message(message.chat.id, m.send_all_tables(r.json()))

@bot.message_handler(regexp='^\/roll .{1,20}$')
def roll_dice(message: Message):
    pass

@bot.message_handler(regexp='^\/show .{1,20}$')
def show_entries(message: Message):
    pass

@bot.message_handler(commands=['tags'])
def show_all_tags(message: Message):
    pass

@bot.message_handler(regexp='^\/tag .{1,20}$')
def search_by_tag(message: Message):
    pass


class Command(BaseCommand):
    help = "Run the bot"
    
    def handle(self, *args, **options):
        bot.polling()