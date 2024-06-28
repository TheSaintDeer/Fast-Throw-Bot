import requests
import telebot
from telebot.types import Message

import local_settings
import messages as m


bot = telebot.TeleBot(local_settings.TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.send_message(message.chat.id, m.start_answer)

@bot.message_handler(commands=['tables'])
def roll_dice(message: Message):
    pass

@bot.message_handler(regexp='^\/roll_.{1,20}$')
def roll_dice(message: Message):
    pass

@bot.message_handler(regexp='^\/show_.{1,20}$')
def roll_dice(message: Message):
    pass

if __name__ == "__main__":
    bot.polling()