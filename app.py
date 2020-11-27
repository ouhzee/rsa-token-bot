from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatAction, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, ConversationHandler
from telegram.utils import helpers
from functools import wraps
import Role, messageformat, logging, re, dbhelper

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


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
    chat_name = re.findall(r"^\S*..", update.effective_chat.firs_name + " " + update.effective_chat.last_name)[0]
    url = context.user_data.get('url')
    sdtid = context.user_data.get('file')
    username = context.user_data.get('username')
    setpin = context.user_data.get('setpin')
    grup = context.user_data.get('grup')

    #create instance
    user = Role.Verify(chat_id)
    #download if sdtid
    if sdtid:
        downloadFile(update, context)

    user.registerToken(chat_id=chat_id, chat_name=chat_name, username=username, setpin=setpin, team_name=grup, token=url, sdtid=sdtid)
    update.message.reply_text(text=f'done, {username} to {grup} imported.\n Now you can register your group chat or this chat to your corresponding token')


def conv_token(update, context):
    
    reply = "Great, now please provide username that'll be used to login.\nPlease don't contain any spaces"
    reg = re.match(r'http:\/\/127\.0\.0\.1\/securid.*', update.message.text)

    #check if sdtid is sent
    if update.message.document:
        if update.message.document.mime_type('sdtid'):
            context.user_data['file'] = update.message.document.file_id
            update.message.reply_text(text=f"{reply}", parse_mode=ParseMode.HTML)
            return USERNAME
        else:
            update.message.reply_text(text="File format not sdtid, please send again")
            return TOKEN
    elif reg:
        context.user_data['url'] = update.message.text
        update.message.reply_text(text=f"{reply}", parse_mode=ParseMode.HTML)
        return USERNAME
    else:
        update.message.reply_text(text="i don't understand url you were given, please send again")
        return TOKEN


def conv_username(update, context):
    
    context.user_data['username'] = update.message.text
    reply = "Okay, next one is pin of your token.\nRemember, don't contain any spaces"

    update.message.reply_text(text=f"{reply}", parse_mode=ParseMode.HTML)
    return SETPIN

def conv_setpin(update, context):
    context.user_data['setpin'] = update.message.text
    listgrup = Role.Role.listToken()
    reply = "Terakhir bos, pilih team/grup di bawah.\nCopy / sentuh(kalo pake hp auto copied) nama grupnya, paste terus kirim.\n"

    update.message.reply_text(text=f"{reply}{listgrup[1]}\n\nKalo gaada timnya, kirim aja nama tim/dept nya nanti dibuatkan yang baru")

    return GRUP

def conv_grup(update, context):
    context.user_data['grup'] = update.message.text
    reply = "Importing your token . . . ."
    update.message.reply_text(text=reply)
    return IMPORTTOKEN

@send_action(ChatAction.TYPING)
def registerchat_handler(update, context):
    chat_id = update.effective_chat.id
    role = Role.Verify(chat_id)
    hasil = role.listToken()
    keyboardmarkup = hasil[0]
    teks = hasil[1]

    update.message.reply_text(text=f"Choose one of these token by pressing the menu below.\n<code>{teks}</code>", reply_markup=keyboardmarkup,parse_mode=ParseMode.HTML)

def reqtoken_handler(update, context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id)
    passcode = user.reqPasscode(chat_id)
    if not passcode:
        update.message.reply_text(text=f"Sorry, this chat/group does not belong to any token.\n please register by clicking this /registerchat", parse_mode=ParseMode.HTML)
    update.message.reply_text(text=f"Here is the passcode <code>{passcode}</code>", parse_mode=ParseMode.HTML)

def about_handler(update, context):
    pass

def buttonPressedUser(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    callbackdata = query.data
    from_user = query.from_user.username
    chat_title = query.message.chat.title
    from_requestor = query.from_user.first_name + " " + query.from_user.last_name

    query.answer()
    
    #user klik back to main menu button
    if callbackdata == 'main':
        keyboardmarkup = messageformat.backToMainMenu()
        query.edit_message_reply_markup(reply_markup=keyboardmarkup)

    #user klik owner buttonmenu
    elif re.match(r"send.*", callbackdata):
        #regex to match callback data
        token = re.findall(r"send(.*)", callbackdata)[0]
        db = dbhelper.Database()
        db.connection()
        ownerchat = db.getOwnerChatid(token)
        
        #send notif to owner
        #if coming from private
        if update.effective_chat.type == 'private':
            approvebutton = messageformat.buttonFromOwner(userchat_id=chat_id, chat_name=from_requestor, owner_id=ownerchat[0])
            context.bot.send_message(chat_id=ownerchat[0], text=f"{from_user} {from_requestor} Want to register their chat with your token.\n Approve?", reply_markup=approvebutton)
        #if coming from group/supergroup
        else:
            approvebutton = messageformat.buttonFromOwner(userchat_id=chat_id, chat_name=chat_title, owner_id=ownerchat[0])
            context.bot.send_message(chat_id=ownerchat[0], text=f"{from_user} {from_requestor} Want to register their chat/group {chat_title} with your token.\n Approve?", reply_markup=approvebutton)

        #send message to requestor
        query.message.reply_text(text=f'your request has been sent to {ownerchat[1]}.\nIn addition, please contact the owner')

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
    buttonmarkup = InlineKeyboardMarkup(InlineKeyboardButton(text="Start chat", url=url))

    #check if its group/private chat
    if chat_id < 0:
        print('grup')
        update.message.reply_text(text="Sorry, register token not supported for group type.\nPlease invoke this cmd inside private chat, click button below", reply_markup=buttonmarkup)
        return
    
    else:
        update.message.reply_text(text=f"Hi, Please send me your sdtid file or url token that look like this <code>http://127.0.0.1/securidxxxxx</code>", parse_mode=ParseMode.HTML)
        return TOKEN


def conv_cancel(update, context):
    update.message.reply_text('Okay bye')

    return ConversationHandler.END

def check_handler(update, context):
    print(update.effective_chat.type)
    if update.effective_chat.type == 'private':
        update.message.reply_text(text=f'{update.effective_chat.type}')


###OWNER HANDLER###
def listchat_handler(update, context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id)
    hasil = user.listChat(chat_id=chat_id)

    update.message.reply_text(text=f"Ini list chat yang udah approved \n{hasil[0]}\n Kalo mau unreg chatnya, klik /unregchat")

def unregchat_handler(update,context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id)
    hasil = user.listChat(chat_id=chat_id)

    update.message.reply_text(text=f"{hasil[0]}\n. Klik tombol dibawah buat unregister chatnya", parse_mode=ParseMode.HTML, reply_markup=hasil[1])

def unregtoken_handler(update, context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id)
    user.unregToken(chat_id=chat_id)
    update.message.reply_text(text=f"Done, your token has been unregistered. If you want to import it again, use /registertoken")

def buttonPressedOwner(update, context):
    chat_id = update.effective_chat.id
    user = Role.Verify(chat_id=chat_id)
    userchat_id = re.findall(r"unregchat(.*)")[0]
    user.unregChat(userchat_id)
    update.callback_query.edit_message_reply_markup(reply_markup=None)
    update.message.reply_text(text=f"Done, those chat/group were deleted")
    
    

def main()->None:

    updater = Updater('1081827561:AAHdTmkPfJOP6HAeDuIZYwwUtVA4deVnMgw', use_context=True)
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
                fallbacks=[MessageHandler(Filters.regex(r'cancel'), callback=conv_cancel)]
            )

    ###USER###
    dispatcher.add_handler(CommandHandler('start', start_handler))
    #registertoken cmd
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('registerchat', registerchat_handler))
    dispatcher.add_handler(CommandHandler('token', reqtoken_handler))
    dispatcher.add_handler(CommandHandler('about', about_handler))

    ###OWNER###
    dispatcher.add_handler(CommandHandler('listchat', listchat_handler))
    dispatcher.add_handler(CommandHandler('unregtoken', unregtoken_handler))
    dispatcher.add_handler(CommandHandler('unregchat', unregchat_handler))
    dispatcher.add_handler(CallbackQueryHandler(buttonPressedOwner, pattern='unregchat'))

    ###ADMIN###
    #dispatcher.add_handler(CommandHandler('removetoken'))

    dispatcher.add_handler(CallbackQueryHandler(buttonPressedUser))
    updater.start_polling(clean=True)
    updater.idle()


    ###DEBUG###
    dispatcher.add_handler(CommandHandler('check', check_handler))


if __name__ == '__main__':
    main()