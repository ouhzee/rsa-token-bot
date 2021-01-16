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
    #convert hasilquery from [(token, chat_id, nama_chat), (token, chat_id, nama_chat) to dict {'token': {'chat_id': 'user', 'chat_id': 'user'}}
    for i in hasilquery:
        if i[0] not in tokendict:
            tokendict[i[0]] = {}
            
        if i[1] not in tokendict.get(i[0]):
            tokendict[i[0]][i[1]] = i[2]
    
    # parsing tokendict and create Main Menu button
    print(f"isi dari tokendict {tokendict}")

    for token, chat in tokendict.items():
        teks += f"\n<code>- {token}</code>"

        for chat_id, user in chat.items():
            teks += f"\n<code>   |- {user}</code>"
            buttonlistchat.append(InlineKeyboardButton(text=f"{user}", callback_data=f"unregchat{chat_id}"))
        teks += "\n"

    """for token in tokendict:
        teks += f"\n- {token}"
               
        for user in tokendict.get(token):
            for chat, name in user.items():
                teks += f"\n  |- {token} {name}"
                buttonlistchat.append(InlineKeyboardButton(text=f"{name}", callback_data=f"unregchat{chat}"))
        teks += "\n"""

    markupchat = InlineKeyboardMarkup(buildButton(buttonlistchat,n_col=2))

    return teks, markupchat

def parsingGetOwner(hasilquery):
    '''
    Return tuple (markup, teks)
    '''
    global groupdict
    global markupdept
    teks = ""
    buttonlistdept = []
    print(f'ini groupdict sebelum masuk loop {groupdict}')
    print(f"ini hasilquery {hasilquery}")
    #convert hasilquery [('token', 'namauser', 'nama tim'), ('token', 'namauser', 'nama tim')] to dict {'grup': {'token': 'owner', 'token': 'owner'}}
    for i in hasilquery:                

        

        if i[2] not in groupdict:
            groupdict[i[2]] = {}
            
        if i[0] not in groupdict.get(i[2]):
            groupdict[i[2]][i[0]] = i[1]

    # parsing groupdict and create Main Menu button
    for grup, owner in groupdict.items():
        teks += f"\n- <code>{grup}</code>"
        buttonlistdept.append(InlineKeyboardButton(text=f"{grup}", callback_data=grup))
        
        for token, name in owner.items():
            teks += f"\n<code>  |- {token} {name}</code>"
        teks += "\n"

    markupdept = InlineKeyboardMarkup(buildButton(buttonlistdept, n_col=2))

    #kalo callback == grup
    print(f'ini teks {teks}')
    print(f'ini groupdict {groupdict}')
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
    
    for token, name in groupdict.get(callback_data).items():
        buttonlisttoken.append(InlineKeyboardButton(text=f"{token}",callback_data="send"+token))

    markuptoken = InlineKeyboardMarkup(buildButton(buttonlisttoken, n_col=2, footer_button=backtomainmenu))

    return markuptoken
    
def backToMainMenu():
    return markupdept

def buttonFromOwner(userchat_id, chat_name, owner_id):
    #format callback data = insertchat_id,chat_name,to_owner
    button = [InlineKeyboardButton(text=f"Click to approve", callback_data=f'insert{userchat_id},{chat_name},{owner_id}')]
    markupbutton = InlineKeyboardMarkup(buildButton(button, n_col=1))
    return markupbutton

def parsingPasscode(token):
    return token[0][0]