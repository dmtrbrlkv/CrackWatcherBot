import crack_watch
import json
import urllib.parse
import logging
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument("-t", action="store", default=os.environ.get("TG_TOKEN"))
args = parser.parse_args()

import telebot
TOKEN = args.t
RUTRACKER_URL = "https://rutracker.org/forum/tracker.php?nm="

bot = telebot.TeleBot(TOKEN)
cw = crack_watch.CrackWatch()


keyboard = telebot.types.ReplyKeyboardMarkup()
keyboard.row('/Last_cracked', '/Last_cracked_AAA')
keyboard.row('/AAA_crack_subscribe', '/All_crack_subscribe')
keyboard.row('/Subscribe_stat', '/Unsubscribe')


def load_subscribe():
    with open("app/subscribe.json") as f:
        subscribe = json.load(f)
    return subscribe


subscribe = load_subscribe()


def add_subscribe(id, is_AAA, subscribe):
    subscribe[str(id)] = is_AAA
    with open("app/subscribe.json", mode="w") as f:
        json.dump(subscribe, f)


def remove_subscribe(id, subscribe):
    if str(id) not in subscribe:
        return
    del subscribe[str(id)]

    with open("app/subscribe.json", mode="w") as f:
        json.dump(subscribe, f)


def get_subscribe_stat(id, subscribe):
    if str(id) not in subscribe:
        return None
    return subscribe[str(id)]


@bot.message_handler(commands=['start'])
def start(message):
    logging.info(f"Start by {message.chat.id}")
    bot.send_message(message.chat.id, 'https://crackwatch.com/ bot', reply_markup=keyboard)


def send_game_info(chat_id, game_info):
    game_msg = game_info.title + "\n" + "Cracked: " + game_info.crack_date.strftime("%d.%m.%Y %X")  + " by " + game_info.groups + "\n" + game_info.url + "\n" + RUTRACKER_URL + urllib.parse.quote(game_info.title)
    bot.send_photo(chat_id, game_info.image, game_msg, reply_markup=keyboard)


def last_cracked(message, is_AAA):
    game_infos = cw.last_cracked_n(is_AAA=is_AAA)
    if game_infos is None:
        bot.send_message(message.chat.id, 'Please retry later', reply_markup=keyboard)
        return

    for game_info in game_infos:
        send_game_info(message.chat.id, game_info)


@bot.message_handler(commands=['Last_cracked'])
def last_cracked_all(message):
    logging.info(f"Last cracked all by {message.chat.id}")
    last_cracked(message, False)


@bot.message_handler(commands=['Last_cracked_AAA'])
def last_cracked_AAA(message):
    logging.info(f"Last cracked AAA by {message.chat.id}")
    last_cracked(message, True)


@bot.message_handler(commands=['AAA_crack_subscribe'])
def AAA_crack_subscribe(message):
    logging.info(f"AAA crack subscribe by {message.chat.id}")
    add_subscribe(message.chat.id, True, subscribe)
    bot.send_message(message.chat.id, 'Successfully subscribed on AAA cracks', reply_markup=keyboard)


@bot.message_handler(commands=['All_crack_subscribe'])
def all_crack_subscribe(message):
    logging.info(f"All crack subscribe by {message.chat.id}")
    add_subscribe(message.chat.id, False, subscribe)
    bot.send_message(message.chat.id, 'Successfully subscribed on all cracks', reply_markup=keyboard)


@bot.message_handler(commands=['Unsubscribe'])
def unsubscribe(message):
    logging.info(f"Unsubscribe by {message.chat.id}")
    remove_subscribe(message.chat.id, subscribe)
    bot.send_message(message.chat.id, 'Successfully unsubscribed', reply_markup=keyboard)


@bot.message_handler(commands=['Subscribe_stat'])
def subscribe_stat(message):
    logging.info(f"Subscribe stat by {message.chat.id}")
    stat = get_subscribe_stat(message.chat.id, subscribe)
    if stat is None:
        bot.send_message(message.chat.id, 'No subscribe', reply_markup=keyboard)
    elif stat:
        bot.send_message(message.chat.id, 'AAA games subscribe', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'All games subscribe', reply_markup=keyboard)




