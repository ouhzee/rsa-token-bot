from telegram.ext import Updater
from telegram import ParseMode
from configparser import ConfigParser
from dbhelper import Database
import argparse

argparser = argparse.ArgumentParser(description="Example list arg", add_help=True)

parser = ConfigParser()
parser.read("config/bot.ini")
bot_token = parser.get("bot","token")
parser.clear()
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher


def notifMaintenance():
	parser.read("config/message.ini")
	
	
	msg = parser.get("bot","notifMaintenance")
	#msg.replace('\\n','\n')
	sticker = parser.get("bot","notifMaintenanceSticker")
	parser.clear()
	db = Database()
	db.connection()
	print(msg)
	listchat_id = db.getAllUserOwner()
	print(listchat_id)
	#send message
	
	for i in listchat_id:
		dispatcher.bot.send_message(chat_id=i, text=msg, parse_mode=ParseMode.HTML)
		dispatcher.bot.send_sticker(chat_id=i, sticker=sticker)
	

def notifUpdate():
	parser.read("config/message.ini")
	msg = parser.get("bot","notifUpdate")
	sticker = parser.get("bot","notifUpdateSticker")
	parser.clear()
	db = Database()
	db.connection()

	listchat_id = db.getAllUserOwner()

	#send message
	#send message
	for i in listchat_id:
		dispatcher.bot.send_message(chat_id=i, text=msg)
		dispatcher.bot.send_sticker(chat_id=i, sticker=sticker)

def tesFunc():
	print("ini tesfunct()")


def main():

	argparser.add_argument('-u', '--update', dest='command', action='store_const', const='notifupdate', help='Send message new feature added')
	argparser.add_argument('-m', '--maintenance', dest='command', action='store_const',const='notifmaintenance', help='Send Maintenance Message and sticker')
	args = argparser.parse_args()

	if args.command == 'notifupdate':
		notifUpdate()
	elif args.command == 'notifmaintenance':
		notifMaintenance()

if __name__ == '__main__':
	main()