from telegram.ext import Updater
from telegram import ParseMode

updater = Updater(token='624508206:AAHnjG3k116QaM8UW1pRELGwqUWAJ3ukipo', use_context=True)
dispatcher = updater.dispatcher

#dispatcher.bot.send_message(chat_id=-1001124606422, text="tolong colokno adzin. this is passive message")

with open('whitelist.txt', 'r') as w:
	line = w.read();
	WHITELIST = [int(i) for i in line.split()]
	for i in WHITELIST:
		
		dispatcher.bot.send_message(chat_id=i, text="Hi, bot new feature added.\nIt can now able to take multiple token to be imported to this bot.\n\nInvoke /start to try it.\n\nBisa baca disini ya pak /about")
		dispatcher.bot.send_sticker(chat_id=i, sticker="CAACAgUAAxkBAAIE31_DmQNT1CFcKYQVayyOmnuFJM_1AAIwAAP6nYY8U_ofj-2ek30eBA")
		"""dispatcher.bot.send_message(chat_id=i, text="Hi, there will be update coming out and it'll take aproximately about 10-20 minutes at 20:00.\n\nBot will ignore any command during that timeframe", parse_mode=ParseMode.HTML)"""

