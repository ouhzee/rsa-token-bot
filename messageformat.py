from telegram import InlineKeyboardButton, InlineKeyboardMarkup


groupdict = {}
markupdept = None

def buildButton(buttons, n_col, header_button=None, footer_button=None):
    menu = [buttons[i:i + n_col] for i in range(0, len(buttons), n_col)]
    if footer_button:
        menu.append([footer_button])
    return menu

def parsingList(hasilquery):
    tokendict = {}
    teks = ""
    buttonlistchat = []
    #convert hasilquery from [(token, chat_id, nama_chat), (token, chat_id, nama_chat) to dict {'token': [{'chat_name': chat_id}, {'chat_name': chat_id}]}
    for i in hasilquery:
        if i[0] not in tokendict:
            token[i[0]] = []
        if i[0] in tokendict:
            tokendict[i[0]].append({i[1]:i[2]})
    
    # parsing tokendict and create Main Menu button
    for token in tokendict:
        teks += f"\n- {token}"
               
        for user in tokendict.get(token):
            for chat, name in user.items():
                teks += f"\n  |- {token} {name}"
                buttonlistchat.append(InlineKeyboardButton(text=f"{name}", callback_data="unregchat"+chat))
        teks += "\n"

    markupchat = InlineKeyboardMarkup(buildButton(buttonlistchat,n_col=2))

    return teks,markupchat

def parsingGetOwner(hasilquery):
    '''
    Return tuple (markup, teks)
    '''
    global groupdict
    global markupdept
    teks = ""
    buttonlistdept = []

    #convert hasilquery to dict {'grup': [{'owner': chat_id}, {'owner': chat_id}]}
    for i in hasilquery:
        if i[2] not in groupdict:
            groupdict[i[2]] = []

        if i[2] in groupdict:
            groupdict[i[2]].append({i[1]:i[0]})

    # parsing groupdict and create Main Menu button
    for grup in groupdict:
        teks += f"\n- {grup}"
        buttonlistdept.append(InlineKeyboardButton(text=f"{grup}", callback_data=grup))
        
        for owner in groupdict.get(grup):
            for name, token in owner.items():
                teks += f"\n  |- {token} {name}"
        teks += "\n"

    markupdept = InlineKeyboardMarkup(buildButton(buttonlistdept, n_col=2))

    #kalo callback == grup
    return markupdept, teks

    #keyboard maker

#create Sub-Menu list token
def menuToken(callback_data):
    """This is a function

    Arguments:
        callback_data {str} -- callback_data dari button
    """
    buttonlisttoken = []
    backtomainmenu = InlineKeyboardButton(text=f"<< Back to Group", callback_data='main')
    global groupdict
    
    for owner in groupdict.get(callback_data):
        for name, token in owner.items():
            buttonlisttoken.append(InlineKeyboardButton(text=f"{token}", callback_data="send"+token))

    markuptoken = InlineKeyboardMarkup(buildButton(buttonlisttoken, n_col=2, footer_button=backtomainmenu))

    return markuptoken
    
def backToMainMenu():
    return markupdept

def buttonFromOwner(userchat_id, chat_name, owner_id):
    #format callback data = insertchat_id,chat_name,to_owner
    button = InlineKeyboardMarkup(InlineKeyboardButton(text=f"Click to approve", callback_data=f'insert{userchat_id},{chat_name},{owner_id}'))
    return button

def parsingPasscode(token):
    return token[0][0]