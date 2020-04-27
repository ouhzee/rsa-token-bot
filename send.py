from telegram.ext import Updater
from telegram import ParseMode

updater = Updater(token='624508206:AAHnjG3k116QaM8UW1pRELGwqUWAJ3ukipo', use_context=True)
dispatcher = updater.dispatcher

#dispatcher.bot.send_message(chat_id=-1001124606422, text="tolong colokno adzin. this is passive message")

with open('whitelist.txt', 'r') as w:
	line = w.read();
	WHITELIST = [int(i) for i in line.split()]
	for i in WHITELIST:
		dispatcher.bot.send_message(chat_id=i, text="Hi, connected now.\n<i><b>Read the manual by invoking /help</b></i>", parse_mode=ParseMode.HTML, disable_notification=True)
		dispatcher.bot.send_sticker(chat_id=i, sticker="CAACAgQAAx0CSECS_wACECRefmLAwi1ezZH3x0QWHCJzUUdIHwACDQEAAk4VJwxsdA31ag9tlRgE")
