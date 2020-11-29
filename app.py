from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatAction, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, ConversationHandler
from telegram.utils import helpers
from functools import wraps
import Role, messageformat, logging, re, dbhelper

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

##deeplink urll##
tomybot = 'to-my-bot'

TOKEN, USERNAME, SETPIN, GRUP, IMPORTTOKEN = range(5)

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
    chat_name = re.findall(r"^\S*..", update.effective_chat.first_name + " " + update.effective_chat.last_name)[0]
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

    user.registerToken(chat_id=chat_id, chat_name=chat_name, username=username, setpin=setpin, team_name=grup, token=url, sdtid=sdtid)
    
    update.message.reply_text(text=f'done, {username} to {grup} imported.\n\n Now you can register your this chat or group chat to your corresponding token.\n')
    return ConversationHandler.END


def conv_token(update, context):
    
    reply = "Great, now please provide username that'll be used to login with this token (not telegram username).\n\n<b>Please don't contain any spaces.</b>"
    

    #check if sdtid is sent
    if update.message.document:

        document = update.message.document
        print(update.message.document.mime_type)
        if document.mime_type == 'application/xml' and re.match(r".*sdtid",document.file_name):

            context.user_data['file'] = context.bot.getFile(update.message.document.file_id)
            
            update.effective_message.reply_text(text=f"{reply}", parse_mode=ParseMode.HTML)
            return USERNAME

        else:
            update.message.reply_text(text="File format not sdtid, please send again")
            return TOKEN
    elif re.match(r'http:\/\/127\.0\.0\.1\/securid.*', update.message.text):
        context.user_data['url'] = update.message.text
        update.message.reply_text(text=f"{reply}", parse_mode=ParseMode.HTML)
        return USERNAME
    else:
        update.message.reply_text(text="i don't understand url you were given, please send again")
        return TOKEN


def conv_username(update, context):
    
    context.user_data['username'] = update.message.text
    reply = "Okay, next one is pin of your token.\n\n<b>Remember, don't contain any spaces.</b>"

    update.message.reply_text(text=f"{reply}", parse_mode=ParseMode.HTML)
    return SETPIN

def conv_setpin(update, context):
    context.user_data['setpin'] = update.message.text
    listgrup = Role.Role.listToken()
    reply = "Terakhir bos, pilih team/grup di bawah.\nCopy / sentuh(kalo pake hp auto copied) nama tim dibawah, paste terus kirim. <b>Nama timnya aja, gaperlu <code>|- username namaowner</code>\n"

    update.message.reply_text(text=f"{reply}{listgrup[1]}\n\n<b>Kalo list diatas gaada, kirimin aja nama tim/dept nya nanti dibuatkan yang baru</b>", parse_mode=ParseMode.HTML)

    return GRUP

def conv_grup(update, context):
    context.user_data['grup'] = update.message.text
    reply = "confirm your token information"
    update.message.reply_text(text=f"type <b>okay</b> to {reply}.\n\nUse /cancel to cancel", parse_mode=ParseMode.HTML)
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

    update.message.reply_text(text=f"Choose one of these token by pressing the menu below.\n<code>{teks}</code>", reply_markup=keyboardmarkup,parse_mode=ParseMode.HTML)

@send_action(ChatAction.TYPING)
def listtoken_handler(update, context):
    chat_id = update.effective_chat.id
    role = Role.Verify(chat_id)
    #clear groupdict and button
    messageformat.groupdict = {}
    messageformat.markupdept = {}
    keyboard, teks = role.listToken()

    update.message.reply_text(text=f"Token registered to this bot.\n<code>{teks}</code>", parse_mode=ParseMode.HTML)

def reqtoken_handler(update, context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id)
    passcode = user.reqPasscode(chat_id, nexttoken=None)
    
    if passcode:
        button = []
        #create dict for button
        buttondict = {'next60': 'next 60s', 'next3600': 'next 1h', 'next7200': 'next 2h', 'next14400': 'next 4h'}
        
        #build button for next token from buttondict
        for callbackdata, teks in buttondict.items():
            button.append(InlineKeyboardButton(
                    text=teks, callback_data=callbackdata
                    )
                )
        buttonmarkup = InlineKeyboardMarkup(messageformat.buildButton(button, 2))

        update.message.reply_text(text=f"Here is the passcode <code>{passcode}</code>", parse_mode=ParseMode.HTML, reply_markup=buttonmarkup)
    else:
        update.message.reply_text(text=f"Sorry, this chat/group does not belong to any token.\n please register by clicking this /registerchat", parse_mode=ParseMode.HTML)

def about_handler(update, context):
    teks = "Hi, thankyou for using this bot.\n\nYou can read the tutorial below.\n<a href='https://telegra.ph/RSA-Token-Telegram-Bot-11-29'>Click Here</a> or instant view on phone"
    update.message.reply_text(text=teks, parse_mode=ParseMode.HTML)


def buttonPressedNext(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    callbackdata = query.data
    from_userfirstname = query.from_user.first_name
    nexttoken = int(re.findall(r"next(.*)", callbackdata)[0])
    
    user = Role.Verify(chat_id)
    passcode, waktu = user.reqPasscode(chat_id, nexttoken)

    query.edit_message_reply_markup(reply_markup=None)
    query.message.reply_text(text=f"{from_userfirstname} here is your passcode:\n\n<code>{passcode}active until {waktu}</code>", parse_mode=ParseMode.HTML)

def buttonPressedUser(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    callbackdata = query.data
    from_user = query.from_user.username
    chat_title = query.message.chat.title
    from_requestor = query.from_user.first_name + " " + query.from_user.last_name
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
            print("masuk dalam if private")
            approvebutton = messageformat.buttonFromOwner(userchat_id=chat_id, chat_name=from_requestor, owner_id=ownerchat[0])
            print(f'approvebutton sudah assigned, ini owner_id {owner_id}')
            context.bot.send_message(chat_id=owner_id, text=f"@{from_user} {from_requestor} want to register their chat with your token.\n\n Approve?", reply_markup=approvebutton, parse_mode=ParseMode.HTML)
            print('context bot buat ngirim ke owner')
            
        #if coming from group/supergroup
        else:
            approvebutton = messageformat.buttonFromOwner(userchat_id=chat_id, chat_name=chat_title, owner_id=ownerchat[0])
            context.bot.send_message(chat_id=ownerchat[0], text=f"@{from_user} {from_requestor} want to register their group {chat_title} with your token.\n\n Approve?", reply_markup=approvebutton, parse_mode=ParseMode.HTML)

        #send message to requestor
        print('notif ke requestor')
        query.edit_message_reply_markup(reply_markup=None)
        query.message.reply_text(text=f'your request has been sent to {ownerchat[1]}.\nIn addition, please contact the owner')

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
        update.message.reply_text(text="Sorry, register token not supported for group type.\nPlease invoke this cmd inside private chat, click button below", reply_markup=buttonmarkup)
        return ConversationHandler.END
    
    else:
        db = dbhelper.Database()
        db.connection()
        if db.getOwner(chat_id=chat_id):
            update.message.reply_text(text=f"You have already imported your token.\n\nIf you want to change it, please unregister first then register it again", parse_mode=ParseMode.HTML)
            return ConversationHandler.END
        else:
            update.message.reply_text(text=f"Hi, Please send me your <b>.sdtid</b> file\n\nor url token that look like this \n<code>http://127.0.0.1/securidxxxxx</code>", parse_mode=ParseMode.HTML)
            return TOKEN


def conv_cancel(update, context):
    update.message.reply_text('Okay bye')

    return ConversationHandler.END

def askAdmin_handler(update, context):
    buttonmarkup = InlineKeyboardMarkup.from_button(InlineKeyboardButton(text="Yes", callback_data='notifyadmin'))

    update.message.reply_text(text=f'You want to chat with admin?\n\nThis will notify admin and reply your message', reply_markup=buttonmarkup)

def buttonPressedNotify(update, context):
    name = update.callback_query.from_user.first_name
    username = update.callback_query.from_user.username
    chat_title = update.callback_query.message.chat.title

    context.bot.send_message(chat_id=166942761 ,text=f'Manggil bos\nGroup: {chat_title}\nFrom: {name} @{username}.')
    update.callback_query.edit_message_reply_markup(reply_markup=None)
    update.callback_query.message.reply_text(text="Admin has been notified, please wait")

def addgroup_handler(update, context):
    if update.message.new_chat_member[0].id == context.bot.get_me.id:
        update.message.reply_text(text=f"Hi, thankyou for adding me to your group.\n\nThere are three basic cmd, you can access it by clicking forwardslash(/) next to emoji icon below")

###DEBUG###
def check_handler(update, context):
    print(update.effective_chat.type)
    if update.effective_chat.type == 'private':
        update.message.reply_text(text=f'{update.effective_chat.type}')



###OWNER HANDLER###
def listchat_handler(update, context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id)
    hasil = user.listChat(chat_id=chat_id)

    update.message.reply_text(text=f"Ini list chat yang udah approved \n{hasil}\n Kalo mau unreg chatnya, klik /unregchat", parse_mode=ParseMode.HTML)

def unregchat_handler(update,context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id)
    hasil = user.listChat(chat_id=chat_id)

    update.message.reply_text(text=f"Sorry, ths feature still under development")
    #update.message.reply_text(text=f"{hasil[0]}\n. Klik tombol dibawah buat unregister chatnya", parse_mode=ParseMode.HTML, reply_markup=hasil[1])

def unregtoken_handler(update, context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id)
    user.unregToken(chat_id=chat_id)
    update.message.reply_text(text=f"Done, your token has been unregistered.\nYou could always import it again using /registertoken")

def buttonPressedOwner(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    callbackdata = query.data
    user = Role.Verify(chat_id=chat_id)
    #if user unregchat
    if re.match(r"unregchat(.*)", callbackdata):
        userchat_id = re.findall(r"unregchat(.*)")[0]
        user.unregChat(userchat_id)
        update.callback_query.edit_message_reply_markup(reply_markup=None)
        update.message.reply_text(text=f"Done, those chat/group were deleted")
    #if owner klik approve button
    elif re.match(r"insert.*", callbackdata):
        #extract callbackdata from format "insertUserchat_id,chat_name,owner_id"
        datachat = re.findall(r"insert(.*)", callbackdata)
        #convert it to list of string
        hasildatachat = datachat[0].split(',')
        userchat_id = hasildatachat[0]
        userchat_name = hasildatachat[1]
        owner_id = hasildatachat[2]

        #insert to db
        user = Role.Verify(userchat_id)
        user.registerChat(userchat_id, userchat_name, owner_id)
        query.edit_message_reply_markup(reply_markup=None)
        query.message.reply_text(text=f'Done, those chat has been registered to your token.\nYou can unregister by /unregchat', parse_mode=ParseMode.HTML)

        context.bot.send_message(chat_id=userchat_id, text=f"Owner has approved this chat.\n\nYou can invoke /token or just send text containing <code>token</code>.", parse_mode=ParseMode.HTML)
    
    

def main()->None:

    updater = Updater('624508206:AAHnjG3k116QaM8UW1pRELGwqUWAJ3ukipo', use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
                entry_points=[CommandHandler('registertoken', registertoken_handler)],
                states={
                    TOKEN: [MessageHandler(Filters.all, callback=conv_token)],
                    USERNAME: [MessageHandler(Filters.all, callback=conv_username)],
                    SETPIN: [MessageHandler(Filters.all, callback=conv_setpin)],
                    GRUP: [MessageHandler(Filters.all, callback=conv_grup)],
                    IMPORTTOKEN: [MessageHandler(Filters.all, callback=importToken)]
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
    dispatcher.add_handler(CommandHandler('about', about_handler))
    dispatcher.add_handler(CallbackQueryHandler(buttonPressedNext, pattern='next'))
    #notify admin
    dispatcher.add_handler(CommandHandler('askadmin', askAdmin_handler))
    dispatcher.add_handler(CallbackQueryHandler(buttonPressedNotify, pattern='notifyadmin'))
    dispatcher.add_handler(CommandHandler('listtoken', listtoken_handler))
    #if bot added to group
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, addgroup_handler))

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