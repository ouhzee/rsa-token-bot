"""from abc import abstractmethod, ABC, ABCMeta

class Tool(ABC):
    
    @abstractmethod
    def mouseDown(self):
        pass

    @abstractmethod
    def mouseUp(self):
        pass


class SelectionTool(Tool):
    #override abstractmethod
    def mouseDown(self):
        print("selection icon")

    def mouseUp(self):
        print("draw dash rectangle")


class BrushTool(Tool):
    #override abstractmethod
    def mouseDown(self):
        print("brush icon")

    def mouseUp(self):
        print("draw a line")


class Canvas():
    currentTool = None
    def mouseUp(self):
        self.currentTool.mouseUp()

    def mouseDown(self):
        self.currentTool.mouseDown()

    def setCurrentTool(self, currentTool):
        self.currentTool = currentTool


canvas = Canvas()
canvas.setCurrentTool(BrushTool())
canvas.mouseDown()
print(issubclass(BrushTool, Tool))"""

"""import sqlite3
from dbhelper import Database

conn = sqlite3.connect('rsatoken.db')
cur = conn.cursor()
cur.execute("select chat_id, chat_name from user where to_owner = 123")
print(cur.fetchall())"""
#x = [x[0] for x in cur.fetchall()]
#print(x)


##Tes storing conversation using callback
"""from uuid import uuid4
from telegram.ext import Updater, CommandHandler

def put(update, context):
    ##Usage: /put value
    # Generate ID and seperate value from command
    key = str(uuid4())
    # We don't use context.args here, because the value may contain whitespaces
    value = update.message.text.partition(' ')[2]

    # Store value
    context.user_data['token'] = value
    #context.user_data['url'] = "http"

    update.message.reply_text(text=f"{value} ini contex.args {context.args} ini context.user_data {context.user_data}")

def get(update, context):
    #Usage: /get uuid
    # Seperate ID from command
    #key = context.args[0]

    # Load value
    token = context.user_data.get('token', 'Not found')
    url = context.user_data.get('url')
    update.message.reply_text(text=f"ini token {token} ini url {url}")
    context.user_data.clear()

if __name__ == '__main__':
    updater = Updater('1081827561:AAHdTmkPfJOP6HAeDuIZYwwUtVA4deVnMgw', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('put', put))
    dp.add_handler(CommandHandler('get', get))

    updater.start_polling()
    updater.idle()"""

###Tes deeplinking to button###
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""Bot that explains Telegram's "Deep Linking Parameters" functionality.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Deep Linking example. Send /start to get the link.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Updater, CommandHandler, Filters, CallbackContext

# Enable logging
from telegram.utils import helpers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define constants that will allow us to reuse the deep-linking parameters.
CHECK_THIS_OUT = 'check-this-out'
USING_ENTITIES = 'using-entities-here'
SO_COOL = 'so-cool'


def start(update: Update, context: CallbackContext) -> None:
    """Send a deep-linked URL when the command /start is issued."""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.get_me().username, CHECK_THIS_OUT, group=True)
    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text='Continue here!', url=url)
    )
    text = "Feel free to tell your friends about it:\n\n" + url
    update.message.reply_text(text=text, reply_markup=keyboard)


def deep_linked_level_1(update: Update, context: CallbackContext) -> None:
    """Reached through the CHECK_THIS_OUT payload"""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.get_me().username, SO_COOL)
    text = (
        "Awesome, you just accessed hidden functionality! "
        " Now let's get back to the private chat."
    )
    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text='Continue here!', url=url)
    )
    update.message.reply_text(text, reply_markup=keyboard)


def deep_linked_level_2(update: Update, context: CallbackContext) -> None:
    """Reached through the SO_COOL payload"""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.get_me().username, USING_ENTITIES)
    text = f"You can also mask the deep-linked URLs as links: [▶️ CLICK HERE]({url})."
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


def deep_linked_level_3(update: Update, context: CallbackContext) -> None:
    """Reached through the USING_ENTITIES payload"""
    payload = context.args
    update.message.reply_text(
        f"Congratulations! This is as deep as it gets 👏🏻\n\nThe payload was: {payload}"
    )


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1081827561:AAHdTmkPfJOP6HAeDuIZYwwUtVA4deVnMgw", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # More info on what deep linking actually is (read this first if it's unclear to you):
    # https://core.telegram.org/bots#deep-linking

    # Register a deep-linking handler
    

    # This one works with a textual link instead of an URL
    dispatcher.add_handler(CommandHandler("start", deep_linked_level_2, Filters.regex(SO_COOL)))

    # We can also pass on the deep-linking payload
    dispatcher.add_handler(
        CommandHandler("start", deep_linked_level_3, Filters.regex(USING_ENTITIES), pass_args=True)
    )

    # Make sure the deep-linking handlers occur *before* the normal /start handler.
    dispatcher.add_handler(CommandHandler("start", start))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()