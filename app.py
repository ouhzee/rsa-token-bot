from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatAction, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, ConversationHandler
from telegram.utils import helpers
from functools import wraps
from configparser import ConfigParser
import Role, messageformat, logging, re, dbhelper

parser = ConfigParser()
parser.read("config/bot.ini")
bot_token = parser.get("bot", "token")
parser.clear()


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

##deeplink urll##
tomybot = 'to-my-bot'

TOKEN, USERNAME, SETPIN, GRUP, IMPORTTOKEN = range(5)

def open_message(section:str, option:str)->str:
    parser.read("config/message.ini")
    msg = parser.get(section, option)
    parser.clear()
    return msg

def send_action(action):
    
    def decorator(func):
        
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator

def downloadFile(update, context):
    file = context.bot.getFile(context.user_data.get('file'))
    username = context.user_data.get('username')
    file.download(custom_path=f'sdtid/{username}.sdtid')
    return


def importToken(update, context):
    chat_id = update.effective_message.chat_id
    if update.effective_chat.last_name:
        chat_name = re.findall(r"^\S*..", update.effective_chat.first_name + " " + update.effective_chat.last_name)[0]
    else:
        chat_name = re.findall(r"^\S*..", update.effective_chat.first_name)[0]
    url = context.user_data.get('url')
    sdtid = context.user_data.get('file')
    username = context.user_data.get('username')
    setpin = context.user_data.get('setpin')
    grup = context.user_data.get('grup')

    #create instance
    user = Role.Verify(chat_id)
    #download if sdtid
    if sdtid:
        sdtid.download(f'sdtid/{username}.sdtid')
    print(type(grup))
    user.registerToken(chat_id=chat_id, chat_name=chat_name, username=username, setpin=setpin, team_name=grup, token=url, sdtid=sdtid)
    
    msg = open_message("user","importtoken")
    #update.message.reply_text(text=f'done, {username} to {grup} imported.\n\n Now you can register your this chat or group chat to your corresponding token.\n')
    update.message.reply_text(text=msg.format(username, grup))
    return ConversationHandler.END


def conv_token(update, context):    

    #check if sdtid is sent
    if update.message.document:

        document = update.message.document
        print(update.message.document.mime_type)
        
        if document.mime_type == "application/xml" or document.mime_type == "application/octet-stream" and re.match(r".*sdtid",document.file_name):
            msg = open_message("user","convtoken")
            context.user_data['file'] = context.bot.getFile(update.message.document.file_id)
            
            update.effective_message.reply_text(text=msg, parse_mode=ParseMode.HTML)
            return USERNAME

        else:
            msg = open_message("user","convtokenfile")
            update.message.reply_text(text=msg)
            return TOKEN

    elif re.match(r'http:\/\/127\.0\.0\.1\/securid.*', update.message.text):
        
        context.user_data['url'] = update.message.text
        msg = open_message("user","convtoken")
        update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)
        return USERNAME

    else:
        msg = open_message("user", "convtokenurl")
        update.message.reply_text(text=msg)
        return TOKEN


def conv_username(update, context):
    
    context.user_data['username'] = update.message.text
    msg = open_message("user","convusername")

    update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)
    return SETPIN

def conv_setpin(update, context):
    context.user_data['setpin'] = update.message.text
    listgrup = Role.Role.listToken()
    msg = open_message("user","convsetpin")

    #update.message.reply_text(text=f"{reply}{listgrup[1]}\n\n<b>Kalo list diatas gaada, kirimin aja nama tim/dept nya nanti dibuatkan yang baru</b>\n\n Click /cancel to cancel", parse_mode=ParseMode.HTML)
    update.message.reply_text(text=msg.format(listgrup[1]), parse_mode=ParseMode.HTML)

    return GRUP

def conv_grup(update, context):
    context.user_data['grup'] = update.message.text
    reply = "confirm your token information"
    msg = open_message("user","convgrup")
    
    #update.message.reply_text(text=f"type <b>okay</b> to {reply}.\n\nUse /cancel to cancel", parse_mode=ParseMode.HTML)
    update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)
    return IMPORTTOKEN

@send_action(ChatAction.TYPING)
def registerchat_handler(update, context):
    chat_id = update.effective_chat.id
    role = Role.Verify(chat_id)
    #clear groupdict and button
    messageformat.groupdict = {}
    messageformat.markupdept = {}
    hasil = role.listToken()
    keyboardmarkup = hasil[0]
    teks = hasil[1]
    msg = open_message("alluser", "registerchat")
    update.message.reply_text(text=msg.format(teks), reply_markup=keyboardmarkup,parse_mode=ParseMode.HTML)

@send_action(ChatAction.TYPING)
def listtoken_handler(update, context):
    chat_id = update.effective_chat.id
    role = Role.Verify(chat_id)
    #clear groupdict and button
    messageformat.groupdict = {}
    messageformat.markupdept = {}
    keyboard, teks = role.listToken()
    msg = open_message("alluser","listtoken")

    #update.message.reply_text(text=f"Token registered to this bot.\n<code>{teks}</code>", parse_mode=ParseMode.HTML)
    update.message.reply_text(text=msg.format(teks), parse_mode=ParseMode.HTML)

def reqtoken_handler(update, context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id)
    hasilpasscode = user.reqPasscode(chat_id, nexttoken=None)
    
    if hasilpasscode:
        passcode = hasilpasscode[0]
        username = hasilpasscode[1]
        button = []
        msg = open_message("user","reqtoken")
        #create dict for button
        buttondict = {'next60': 'next 60s', 'next3600': 'next 1h', 'next7200': 'next 2h', 'next14400': 'next 4h'}
        
        #build button for next token from buttondict
        for callbackdata, teks in buttondict.items():
            button.append(InlineKeyboardButton(
                    text=teks, callback_data=callbackdata
                    )
                )
        buttonmarkup = InlineKeyboardMarkup(messageformat.buildButton(button, 2))

        #update.message.reply_text(text=f"<code>username: {username}</code>\nHere is the passcode <code>{passcode}</code>", parse_mode=ParseMode.HTML, reply_markup=buttonmarkup)
        update.message.reply_text(text=msg.format(username, passcode), parse_mode=ParseMode.HTML, reply_markup=buttonmarkup)
    else:
        msg = open_message("user","reqtokennotreg")
        #update.message.reply_text(text=f"Sorry, this chat/group does not belong to any token.\n please register by clicking this /registerchat", parse_mode=ParseMode.HTML)
        update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)

def about_handler(update, context):
    #teks = "Hi, thankyou for using this bot.\n\nYou can read the tutorial below.\n<a href='https://telegra.ph/RSA-Token-Telegram-Bot-01-21'>Click Here</a> or instant view on the phone.\n\nTanya2 pake /askadmin.\nList cmd yg gaada di pojok, pake /start\n\n<code>made by zee with 🐍</code>\n\n."
    msg = open_message("alluser","about")
    update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)


def donate_handler(update, context):
    msg = open_message("alluser","donate")
    update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)


def buttonPressedNext(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    callbackdata = query.data
    from_userfirstname = query.from_user.first_name
    nexttoken = int(re.findall(r"next(.*)", callbackdata)[0])
    msg = open_message("user","reqtokennext")
    
    user = Role.Verify(chat_id)
    passcode, waktu, username = user.reqPasscode(chat_id, nexttoken)

    query.edit_message_reply_markup(reply_markup=None)
    #query.message.reply_text(text=f"<code>username: {username}</code>\n{from_userfirstname} here is your passcode:\n\n<code>{passcode}active until {waktu}</code>", parse_mode=ParseMode.HTML)
    query.message.reply_text(text=msg.format(username, from_userfirstname, passcode, waktu), parse_mode=ParseMode.HTML)

def buttonPressedUser(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    callbackdata = query.data
    from_user = query.from_user.username
    chat_title = query.message.chat.title
    if query.from_user.last_name:
        from_requestor = query.from_user.first_name + " " + query.from_user.last_name
    else:
        from_requestor = query.from_user.first_name
    print('didalam buttonPressedUser method')
    query.answer()
    
    #user klik back to main menu button
    if callbackdata == 'main':
        keyboardmarkup = messageformat.backToMainMenu()
        query.edit_message_reply_markup(reply_markup=keyboardmarkup)

    #user klik owner buttonmenu
    elif re.match(r"send.*", callbackdata):
        print("masuk elif match send")
        #regex to match callback data
        token = re.findall(r"send(.*)", callbackdata)[0]
        db = dbhelper.Database()
        db.connection()
        ownerchat = db.getOwnerChatid(token)
        print(ownerchat)
        owner_id = ownerchat[0]
        
        #send notif to owner
        #if coming from private
        if update.effective_chat.type == 'private':
            msg = open_message("owner","reqapprovalchat")
            print("masuk dalam if private")
            approvebutton = messageformat.buttonFromOwner(userchat_id=chat_id, chat_name=from_requestor, owner_id=ownerchat[0])
            print(f'approvebutton sudah assigned, ini owner_id {owner_id}, ini approvedbutton {approvebutton}')

            #context.bot.send_message(chat_id=owner_id, text=f"@{from_user} {from_requestor} want to register their chat with your token.\n\n Approve?", reply_markup=approvebutton, parse_mode=ParseMode.HTML)
            context.bot.send_message(chat_id=owner_id, text=msg.format(from_user, from_requestor), reply_markup=approvebutton, parse_mode=ParseMode.HTML)
            print('context bot buat ngirim ke owner')
            
        #if coming from group/supergroup
        else:
            approvebutton = messageformat.buttonFromOwner(userchat_id=chat_id, chat_name=chat_title, owner_id=ownerchat[0])
            msg = open_message("owner","reqapprovalgroup")

            #context.bot.send_message(chat_id=ownerchat[0], text=f"@{from_user} {from_requestor} want to register their group {chat_title} with your token.\n\n Approve?", reply_markup=approvebutton, parse_mode=ParseMode.HTML)
            context.bot.send_message(chat_id=ownerchat[0], text=msg.format(from_user,from_requestor,chat_title), reply_markup=approvebutton, parse_mode=ParseMode.HTML)

        #send message to requestor
        print('notif ke requestor')
        query.edit_message_reply_markup(reply_markup=None)
        msg = open_message("user","requestor")
        query.message.reply_text(text=msg.format(ownerchat[1]))
        #query.message.reply_text(text=f'your request has been sent to {ownerchat[1]}.\nIn addition, please contact the owner')

        #clear groupdict and button
        messageformat.groupdict = {}
        messageformat.markupdept = {}

    
    
    #klik menutoken
    else:
        keyboardmarkup = messageformat.menuToken(callbackdata)
        query.edit_message_reply_markup(reply_markup=keyboardmarkup)


@send_action(ChatAction.TYPING)
def start_handler(update, context):
    chat_id = update.message.chat.id
    user = Role.Verify(chat_id)
    menu = user.menu()

    update.message.reply_text(text=f"{menu}\n\nYou can read the tutorial here /about", parse_mode=ParseMode.HTML)


@send_action(ChatAction.TYPING)
def registertoken_handler(update, context):

    chat_id = update.effective_chat.id
    chat_name = update.effective_chat.title
    #create deeplink
    url = helpers.create_deep_linked_url(context.bot.get_me().username)
    #create button with deeplink to bot
    buttonmarkup = InlineKeyboardMarkup.from_button(InlineKeyboardButton(text="Start chat", url=url))

    #check if its group/private chat
    if update.effective_chat.type != 'private':
        print('grup')
        msg = open_message("user","regtokengroup")
        #update.message.reply_text(text="Sorry, register token not supported for group type.\nPlease invoke this cmd inside private chat, click button below", reply_markup=buttonmarkup)
        update.message.reply_text(text=msg, reply_markup=buttonmarkup)
        return ConversationHandler.END
    
    else:
        db = dbhelper.Database()
        db.connection()
        if db.getOwner(chat_id=chat_id):
            msg = open_message("owner","regtoken")
            #update.message.reply_text(text=f"You have already imported your token.\n\nIf you want to change it, please unregister first then register it again", parse_mode=ParseMode.HTML)
            update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)
            return ConversationHandler.END
        else:
            msg = open_message("user","regtoken")
            #update.message.reply_text(text=f"Hi, Please send me your <b>.sdtid</b> file\n\nor url token that look like this \n<code>http://127.0.0.1/securidxxxxx</code>\n\n Click /cancel to cancel", parse_mode=ParseMode.HTML)
            update.message.reply_text(text=msg, parse_mode=ParseMode.HTML)
            return TOKEN


def conv_cancel(update, context):
    update.message.reply_text(open_message("alluser","cancel"))

    return ConversationHandler.END

def askAdmin_handler(update, context):
    buttonmarkup = InlineKeyboardMarkup.from_button(InlineKeyboardButton(text="Yes", callback_data='notifyadmin'))
    msg = open_message("alluser","askadmin")
    
    #update.message.reply_text(text=f'You want to chat with admin?\n\nThis will notify admin and reply your message', reply_markup=buttonmarkup)
    update.message.reply_text(text=msg, reply_markup=buttonmarkup)

def buttonPressedNotify(update, context):
    name = update.callback_query.from_user.first_name
    username = update.callback_query.from_user.username
    chat_title = update.callback_query.message.chat.title
    
    if update.effective_chat.type != 'private':
        msg = open_message("alluser","notifyadmingroup")
        url = helpers.create_deep_linked_url(context.bot.get_me().username)
        buttonmarkup = InlineKeyboardMarkup.from_button(InlineKeyboardButton(text="Start chat", url=url))
        
        context.bot.send_message(chat_id=166942761 ,text=f'Manggil bos\nGroup: {chat_title}\nFrom: {name} @{username}.')
        update.callback_query.edit_message_reply_markup(reply_markup=None)
        #update.callback_query.message.reply_text(text="Admin has been notified, please wait.\n\nPlease issue /start on the button below to initiate conversation with admin.\nIf you have done this before, it's not necessary.", reply_markup=buttonmarkup)
        update.callback_query.message.reply_text(text=msg, reply_markup=buttonmarkup)
    else:
        msg = open_message("alluser","notifyadmin")
        context.bot.send_message(chat_id=166942761 ,text=f'Manggil bos\nGroup: {chat_title}\nFrom: {name} @{username}.')
        update.callback_query.edit_message_reply_markup(reply_markup=None)
        #update.callback_query.message.reply_text(text="Admin has been notified, please wait.")
        update.callback_query.message.reply_text(text=msg)

def addgroup_handler(update, context):
    if update.message.new_chat_members[0].id == context.bot.get_me().id:
        msg = open_message("alluser","addgroup")
        #update.message.reply_text(text=f"Hi, thankyou for adding me to your group.\n\nThere are three basic cmd, you can access it by clicking forwardslash<code>(/)</code> next to emoji icon below")
        update.message.reply_text(text=msg)

###DEBUG###
def check_handler(update, context):
    print(update.effective_chat.type)
    if update.effective_chat.type == 'private':
        update.message.reply_text(text=f'{update.effective_chat.type}')



###OWNER HANDLER###
def listchat_handler(update, context, unreg=False):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id)
    listchat, markupchat = user.listChat(chat_id=chat_id)
    print(listchat)

    if unreg:
        #update.message.reply_text(text=f"Ini list chat yang udah approved \n{listchat}\n <b>Klik button di bawah buat unreg chat yang lu approve boss.</b>", reply_markup=markupchat,parse_mode=ParseMode.HTML)
        msg = open_message("owner","listchatunreg")
        update.message.reply_text(text=msg.format(listchat), reply_markup=markupchat,parse_mode=ParseMode.HTML)
    else:
        #update.message.reply_text(text=f"Ini list chat yang udah approved \n{listchat}\n Kalo mau unreg chatnya, klik /unregchat", parse_mode=ParseMode.HTML)
        msg = open_message("owner","listchat")
        update.message.reply_text(text=msg.format(listchat), parse_mode=ParseMode.HTML)
    
    return


def unregchat_handler(update,context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id).currentRole
    print("ini tipe instance user >> {}".format(type(user)))
    
    if isinstance(user, Role.Owner):
        listchat_handler(update=update, context=context, unreg=True)

    elif isinstance(user, Role.User):
        print("masu isinstance user role")
        if user.unregChat(chat_id=chat_id):
            msg = open_message("user","unregchat")
            #update.message.reply_text(text="Done, this chat has been unregistered from token.\n You will no longer receive bot update")
            update.message.reply_text(text=msg)
            
        else:
            msg = open_message("user","unregtokennotreg")
            #update.message.reply_text(text="This chat isn't registered to any token yet")
            update.message.reply_text(text=msg)
    return
    #update.message.reply_text(text=f"{hasil[0]}\n. Klik tombol dibawah buat unregister chatnya", parse_mode=ParseMode.HTML, reply_markup=hasil[1])


def unregtoken_handler(update, context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id)
    user.unregToken(chat_id=chat_id)
    msg = open_message("owner","unregtoken")
    
    #update.message.reply_text(text=f"Done, your token has been unregistered.\nYou could always import it again using /registertoken")
    update.message.reply_text(text=msg)

def buttonPressedOwner(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    callbackdata = query.data
    user = Role.Verify(chat_id=chat_id)
    #if user unregchat
    if re.match(r"unregchat(.*)", callbackdata):
        userchat_id = re.findall(r"unregchat(.*)", callbackdata)[0]
        msg = open_message("owner","unregchat")
        user.unregChat(userchat_id)
        update.callback_query.edit_message_reply_markup(reply_markup=None)
        #update.callback_query.message.reply_text(text=f"Done, those chat/group were deleted")
        update.callback_query.message.reply_text(text=msg)
    #if owner klik approve button
    elif re.match(r"insert.*", callbackdata):
        #extract callbackdata from format "insertUserchat_id,chat_name,owner_id"
        datachat = re.findall(r"insert(.*)", callbackdata)
        #convert it to list of string
        hasildatachat = datachat[0].split(',')
        userchat_id = hasildatachat[0]
        userchat_name = hasildatachat[1]
        owner_id = hasildatachat[2]
        msgowner = open_message("owner","approvedchat")
        msgrequestor = open_message("user","requestornotify")

        #insert to db
        user = Role.Verify(userchat_id)
        user.registerChat(userchat_id, userchat_name, owner_id)
        query.edit_message_reply_markup(reply_markup=None)
        #query.message.reply_text(text=f'Done, those chat has been registered to your token.\nYou can unregister by /unregchat', parse_mode=ParseMode.HTML)
        query.message.reply_text(text=msgowner, parse_mode=ParseMode.HTML)

        #send notif to requestor
        context.bot.send_message(chat_id=userchat_id, text=msgrequestor, parse_mode=ParseMode.HTML)
        #context.bot.send_message(chat_id=userchat_id, text=f"Owner has approved this chat.\n\nYou can invoke /token or just send text containing <code>token</code>.", parse_mode=ParseMode.HTML)
    
def ping_handler(update, context):
	update.message.reply_text(text="pong 🏓")

def main()->None:

    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
                entry_points=[CommandHandler('registertoken', registertoken_handler)],
                states={
                    TOKEN: [MessageHandler(Filters.document | Filters.text & ~Filters.command, callback=conv_token)],
                    USERNAME: [MessageHandler(Filters.text & ~Filters.command, callback=conv_username)],
                    SETPIN: [MessageHandler(Filters.text & ~Filters.command, callback=conv_setpin)],
                    GRUP: [MessageHandler(Filters.text & ~Filters.command, callback=conv_grup)],
                    IMPORTTOKEN: [MessageHandler(Filters.text & ~Filters.command, callback=importToken)]
                },
                fallbacks=[CommandHandler('cancel', callback=conv_cancel)]
            )

###USER###
    dispatcher.add_handler(CommandHandler('start', start_handler))
    #registertoken cmd
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('registerchat', registerchat_handler))
    dispatcher.add_handler(CommandHandler('token', reqtoken_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(r'.*\stoken|^token|token\s.*'), reqtoken_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(r'ping @wazxwskibot'), ping_handler))
    dispatcher.add_handler(CommandHandler('about', about_handler))
    dispatcher.add_handler(CallbackQueryHandler(buttonPressedNext, pattern='next'))
    #notify admin
    dispatcher.add_handler(CommandHandler('askadmin', askAdmin_handler))
    dispatcher.add_handler(CallbackQueryHandler(buttonPressedNotify, pattern='notifyadmin'))
    dispatcher.add_handler(CommandHandler('listtoken', listtoken_handler))
    #if bot added to group
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, addgroup_handler))
    dispatcher.add_handler(CommandHandler('donate', donate_handler))

###OWNER###
    dispatcher.add_handler(CommandHandler('listchat', listchat_handler))
    dispatcher.add_handler(CommandHandler('unregtoken', unregtoken_handler))
    dispatcher.add_handler(CommandHandler('unregchat', unregchat_handler))
    dispatcher.add_handler(CallbackQueryHandler(buttonPressedOwner, pattern='unregchat|insert'))

###ADMIN###
    #dispatcher.add_handler(CommandHandler('removetoken'))

    dispatcher.add_handler(CallbackQueryHandler(buttonPressedUser))

###DEBUG###
    dispatcher.add_handler(CommandHandler('check', check_handler))


    updater.start_polling(poll_interval=3.0, clean=True)
    updater.idle()


    


if __name__ == '__main__':
    main()
