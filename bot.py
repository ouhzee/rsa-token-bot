import os
import time
import logging
from uuid import uuid4
from functools import wraps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatAction, ParseMode
import json
import re, datetime
from telegram.ext import Updater, CommandHandler, PicklePersistence, MessageHandler, Filters, CallbackQueryHandler, \
    CallbackContext
from telegram import bot

WHITELIST = None
CONVO = None
COUNTER_CONVO = 0
COUNTER = 0

# WHITELIST = [line.rstrip('\n') for line in open('whitelist.txt')]
# WHITELIST = [line.rstrip('\n') for line in open('whitelist.txt')]

persists = PicklePersistence(filename='out', store_chat_data=True)

updater = Updater(token='624508206:AAHnjG3k116QaM8UW1pRELGwqUWAJ3ukipo', use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# noinspection SpellCheckingInspection
def newid():
    global COUNTER
    COUNTER = len(WHITELIST)
    dispatcher.bot.send_message(chat_id=WHITELIST[0], text="yay!")

def manualPage(file):
    '''
    buka file like manualpage or start banner
    :string file:
    :param file:
    '''
    with open(file, 'r') as banner:
        return banner.read()


def req_token():
    comm = os.popen("stoken")
    hasil = comm.read()
    comm.close()
    return hasil


def fetch(save):
    @wraps(save)
    def inner(update, context):
        if update.message.chat.id not in CONVO:

            print("-----------------------------------")
            if update.message.reply_to_message:
                print(">> {0} {1} : @{2}".format(update.message.reply_to_message.from_user.first_name,
                                                 update.message.reply_to_message.from_user.last_name,
                                                 update.message.reply_to_message.from_user.username))
                print(">> {0} -- {1}".format(update.message.reply_to_message.message_id,
                                             update.message.reply_to_message.text))
            print(update.message.photo)

            print("{0} {1} : @{2} {3}".format(update.message.from_user.first_name, update.message.from_user.last_name,
                                              update.message.from_user.username, update.message.chat.title))
            print(" {0} >> {1}".format(update.message.message_id, update.message.text))
            print(" {0}---------------".format(str(datetime.datetime.today().replace(microsecond=0))))
            # return
        return save(update, context)

    return inner


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


def restricted(rest):
    @wraps(rest)
    def wrapped(update, context, *args, **kwargs):
        chat_id = update.message.chat.id
        if chat_id not in WHITELIST:
            print("-----------------------------------")
            print("This Chat not allowed")
            print("{0} {1} : @{2}".format(update.message.from_user.first_name, update.message.from_user.last_name,
                                          update.message.from_user.username))
            print(" {0} >> {1} {2}".format(update.message.message_id, update.message.text, update.message.parse_entities(update.message.entities)))
            print(" {0}---------------".format(str(datetime.datetime.today().replace(microsecond=0))))
            key = [[InlineKeyboardButton("Send data", callback_data='send')]]
            markup = InlineKeyboardMarkup(key)
            update.message.reply_text(
                text="<b>My maker didn't know bout' dis convo.</b>\n\n Contact him then hit this button below\n "
                     "if you wanna use me as your servant.\n Further info, issue <code>/help</code>",
                reply_markup=markup, parse_mode=ParseMode.HTML)
            return
        return rest(update, context, *args, **kwargs)

    return wrapped


def send_data(chat_id):
    updater.bot.send_message(chat_id=166942761, text=chat_id)



@send_action(ChatAction.TYPING)
def button(update, context):
    if update.callback_query.data == 'send':
        #dari_username = update.message.from_user.username
        #print(dari_username)
        update.callback_query.edit_message_reply_markup(reply_markup=None)
        context.bot.send_message(
            chat_id=166942761,
            text="@{1} {3} {4} minta di whitelist {0} {2}".format(update.effective_chat.id,
                                                                  update.callback_query.from_user.username,
                                                                  update.callback_query.message.chat.title,
                                                                  update.callback_query.from_user.first_name,
                                                                  update.callback_query.from_user.last_name))
        #send_data(update.effective_chat.id)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sent. In addition, pls do contact him ")

    else:
        st = os.popen("stoken --next")
        update.callback_query.edit_message_reply_markup(reply_markup=None)
        context.bot.send_message(chat_id=update.effective_chat.id, text="{1} here next `{0}`".format(st.read(), update.callback_query.from_user.first_name), parse_mode=ParseMode.MARKDOWN)
        st.close()


@send_action(ChatAction.TYPING)
def resp_allmessage(update, context, markup):
    if update.message.chat.id in WHITELIST:
        #time.sleep(2)
        update.message.reply_text(text="tap `{0}`".format(req_token()), reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
        print("found")


@send_action(ChatAction.TYPING)
def tes_akses(update, context, ping, test):
#    if ping:
     if ping:
         time.sleep(1)
         update.message.reply_text(text="pong 🏓")
     elif test:
         time.sleep(1)
         update.message.reply_text(text="tis 🍒")


@fetch
# @send_action(ChatAction.TYPING)
# @restricted
def all_message(update, context):
    pass
    if update.message.chat.id in WHITELIST:
        reg = re.match("|".join([".*\stoken", "\stoken", "token\s.*", "token\s", r"\b(token)\b"]), update.message.text)
        key = [[InlineKeyboardButton("Next", callback_data='next token')]]
        markup = InlineKeyboardMarkup(key)
        ping = re.match(r"(@wazxwskibot ping)", update.message.text)
        test = re.match(r"(@wazxwskibot test)", update.message.text)
        if ping or test:
            tes_akses(update, context, ping, test)
            """typ = send_action(ChatAction.TYPING)
            if ping:
                typ(ChatAction.TYPING)
                time.sleep(1)
                update.message.reply_text(text="pong 🏓")
            elif test:
                typ(ChatAction.TYPING)
                update.message.reply_text(text="tis 🍒")"""
    # time.sleep(2)
        elif reg:
            resp_allmessage(update, context, markup)
            """if update.message.chat.id in WHITELIST:
                typ = send_action(ChatAction.TYPING)
                typ(ChatAction.TYPING)
                time.sleep(2)
                update.message.reply_text(text=req_token(), reply_markup=markup)
                print("found")"""


def rep(update, context):
    print(update.message.text)


## all callback func handler starts here

@send_action(ChatAction.TYPING)
@restricted
def token(update, context):
    pass
    hasil = req_token()
    key = [[InlineKeyboardButton("Next", callback_data='next token')]]
    markup = InlineKeyboardMarkup(key)
    typ = send_action(ChatAction.TYPING)
    typ(ChatAction.TYPING)
    time.sleep(2)
    update.message.reply_text(text="tap `{0}`".format(hasil), reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    # context.bot.send_message(chat_id=update.effective_chat.id, text=st.read(), reply_markup=reply_markup)


@send_action(ChatAction.TYPING)
def help_handler(update, context):
    print("-----------------------------------")
    print("This Chat not allowed")
    print("{0} {1} : @{2}".format(update.message.from_user.first_name, update.message.from_user.last_name,
                                  update.message.from_user.username))
    print(" {0} >> {1} {2}".format(update.message.message_id, update.message.text,
                                   update.message.parse_entities(update.message.entities)))
    print(" {0}---------------".format(str(datetime.datetime.today().replace(microsecond=0))))
    typ = send_action(ChatAction.TYPING)
    typ(ChatAction.TYPING)
    time.sleep(2)
    update.message.reply_text(
        text=manualPage('manual.txt'), parse_mode=ParseMode.HTML)


@send_action(ChatAction.TYPING)
def start_handler(update, context):
    update.message.reply_text(text="Pake `/token` om", parse_mode=ParseMode.MARKDOWN)


def echo(update, context: CallbackContext):
    print(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


@send_action(ChatAction.TYPING)
@restricted
def add_group(update, context):
    pass
    if update.message.new_chat_members[0].id == 624508206:
        update.message.reply_text("Hi, ping me")


add_group_handle = MessageHandler(Filters.status_update.new_chat_members, add_group)
dispatcher.add_handler(add_group_handle)
token_handler = CommandHandler('token', token)
dispatcher.add_handler(token_handler)
dispatcher.add_handler(MessageHandler(Filters.text, all_message))
dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('help', help_handler))
dispatcher.add_handler(CallbackQueryHandler(button))
# dispatcher.add_handler(MessageHandler(Filters.text, echo))
updater.start_polling(poll_interval=3.0, clean=True)

# print("ini get chat data "+persists.get_chat_data())
# print("ini get convo "+persists.get_conversations())
# print("ini get user data "+persists.get_user_data())

#	dispatcher.bot.send_message(chat_id=i, text="be back")
#prev = time.time()
while True:
#	now = time.time()
	#if now - prev > 4:
	with open('whitelist.txt', 'r') as w, open('convo.txt', 'r') as c:
		line = w.read()
		convo = c.read()
		WHITELIST = [int(i) for i in line.split()]
		CONVO = [int(i) for i in convo.split()]
		if COUNTER == 0:
			COUNTER = len(WHITELIST)
		elif COUNTER < len(WHITELIST):
			newid()
		else:
			pass
	time.sleep(5)
#	prev = now


updater.idle()


for i in WHITELIST:
	dispatcher.bot.send_sticker(chat_id=i, sticker="CAACAgQAAx0CSECS_wACDtNeWb6o54UNX-J26flFq8mxIECN5QACFwEAAk4VJwzLDYMiyIe7vRgE", disable_notification=True)

print(WHITELIST)
