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
from uuid import uuid4
from telegram.ext import Updater, CommandHandler

def put(update, context):
    """Usage: /put value"""
    # Generate ID and seperate value from command
    key = str(uuid4())
    # We don't use context.args here, because the value may contain whitespaces
    value = update.message.text.partition(' ')[2]

    # Store value
    context.user_data['token'] = value
    #context.user_data['url'] = "http"

    update.message.reply_text(text=f"{value} ini contex.args {context.args} ini context.user_data {context.user_data}")

def get(update, context):
    """Usage: /get uuid"""
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
    updater.idle()