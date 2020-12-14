from abc import abstractclassmethod, ABC
from telegram import bot
import os, messageformat
from dbhelper import Database
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta


class Role(ABC):

    @abstractclassmethod
    def menu(cls):
        pass

    def about(self):
        print("ini about")
        pass

    @classmethod
    def listToken(cls):
        '''
        Return hasilparsing = (markup, teks)
        '''
        db = Database()
        db.connection()
        hasilquery = db.getOwner()
        print(f'ini hasil query {hasilquery}\n masuk messageformat')
        hasilparsing = messageformat.parsingGetOwner(hasilquery)
        print(hasilparsing)
        return hasilparsing

    def reqPasscode(self, tokenid, nexttoken=None):
        '''
        Return passcode->str
        :param tokenid: chat_id of current user
        '''
        db = Database()
        db.connection()
        passcode = None
        button = []

        fetchtoken = db.getUser(tokenid=tokenid)
        if fetchtoken:
            print("masuk if fetchtoken")
            username = messageformat.parsingPasscode(fetchtoken)
            print(f"ini username {username}")

            #condition check callback data button
            if not nexttoken:
            
                cmd = os.popen(f"stoken --rcfile=rcfile/.{username}")
                passcode = cmd.read()
                cmd.close
                print(passcode)
                return passcode, username
            else:
                cmd = os.popen(f"stoken --rcfile=rcfile/.{username} --use-time=+{nexttoken}")
                passcode = cmd.read()
                cmd.close()
                waktu = (datetime.now() + timedelta(seconds=nexttoken)).strftime("%H:%M:%S")
                return passcode, waktu, username
                


        else:
            print("masuk else fetchtoken")
            return None

    def registerToken(self, chat_id: int, chat_name: str, username: str, setpin: int, team_name, token=None, sdtid=None):
        db = Database()
        db.connection()
        #check if this user already have token imported
        if db.getOwner(chat_id=chat_id):
            return False
        self.importToken(username, setpin, sdtid, token)
        db.insertOwner(chat_id, chat_name, team_name, username)
        return

    def importToken(self, username, setpin, sdtid, token):
        cmd = None
        print("masuk importToken")
        if sdtid == None:
            print("masuk if sdtid")
            print(f"isi dari token = {token}")
            cmd = os.popen(f"stoken import --token={token} --new-password=''")
            cmd.close()
            print('cmd close')
        else:
            print('masuk else sdtid')
            os.popen(f"stoken import --file=sdtid/{username}.sdtid --new-password=''")
            
        
        print(f"masuk mv = {username}")
        cmd = os.popen(f"mv $HOME/.stokenrc rcfile/.{username}")
        cmd.close()
        print(f"masuk setpin = {setpin}")
        cmd = os.popen(f"echo 'pin {setpin}' >> rcfile/.{username}")
        cmd.close()
        

        return 

    def registerChat(self, chat_id: int, chat_name: str, owner_id: str):
        '''
        :param token: chat_id of owner
        '''

        db = Database()
        db.connection()
        db.insertUser(chat_id, chat_name, owner_id)


class Admin(Role):
    def menu(self)->str:
        teks = """
        Please click one of the command below.
        <code>
        /registertoken  - register/import token to bot.
        /registerchat   - register current chat/group to available token.
        /removetoken    - remove token.
        </code>
        """
        return teks

    def removeToken(self, chat_id:int):
        db = Database()
        db.connection()
        db.updateOwner(chat_id=chat_id, token=None)


class Owner(Role):
    def menu(self)->str:
        teks = """
        Please type click one of the command below.

/token<code>       - req passcode.</code>
/registertoken<code> - register/import token to bot.</code>
/registerchat<code>  - register current chat/group.</code>
/listtoken<code>     - list available token</code>
/listchat<code>      - list of your approved chat.</code>
/unregtoken<code>  - delete your token.</code>
/unregchat<code>   - unregister approved chat/group.</code>

/askadmin<code>    - chat with admin.</code>
/about<code>       - Tutorial</code>
        
        """
        return teks

    def listChat(self, chat_id):
        '''
        chat_id of owner
        '''
        db = Database()
        db.connection()
        hasil = messageformat.parsingList(db.getUser(chat_id=chat_id))
        return hasil[0]


    def unregToken(self, chat_id:int):
        '''
        chat_id of owner
        '''
        db = Database()
        db.connection()
        db.delTeamOrOwner(chat_id=chat_id)

    def unregChat(self, chat_id):
        '''
        chat_id of user
        '''
        db = Database()
        db.connection()
        db.delUser(chat_id=chat_id)
        return


class User(Role):
    def menu(self)->str:
        teks = """
        Please click one of the command below
        
/token<code>       - req passcode.</code>
/registertoken<code> - register/import token to bot.</code>
/registerchat<code>  - register current chat/group.</code>
/listtoken<code>     - list available token</code>

/askadmin<code>    - chat with admin.</code>
/about<code>       - Tutorial</code>
        """
        return teks

    def tesaja(self):
        db = Database()
        db.connection()
        hasilquery = db.tesquery()
        return hasilquery


class Verify():

    currentRole = None

    def __init__(self, chat_id):
        db = Database()
        db.connection()
        isadmin =  db.getAdmin(chat_id)
        isowner = db.getOwner(chat_id=chat_id)

        if isadmin:
            self.currentRole = Admin()
            print("jadi admin")
        elif isowner:
            self.currentRole = Owner()
            print("jadi owner")
        else:
            self.currentRole = User()
            print("jadi user")

    ###USER###
    def menu(self)-> str:
        hasil = self.currentRole.menu()
        return hasil

    def about(self):
        hasil = self.currentRole.about()
        return hasil

    def listToken(self):
        '''
        Return tuple hasil = (markup, teks)
        '''
        hasil = self.currentRole.listToken()
        return hasil

    def reqPasscode(self, chat_id, nexttoken):
        '''
        :param chat_id: chat_id of current user
        '''
        passcode = self.currentRole.reqPasscode(tokenid=chat_id, nexttoken=nexttoken)
        return passcode

    def registerToken(self, chat_id: int, chat_name: str, username: str, setpin: int, team_name: int, token=None, sdtid=None):
        self.currentRole.registerToken(chat_id, chat_name, username, setpin, team_name, token, sdtid)

    def registerChat(self, chat_id, chat_name, token):
        self.currentRole.registerChat(chat_id, chat_name, token)


    ###Owner###
    def listChat(self, chat_id):
        '''
        chat_id of owner
        '''
        return self.currentRole.listChat(chat_id)

    def unregToken(self, chat_id):
        self.currentRole.unregToken(chat_id)

    def unregChat(self, chat_id:int):
        self.currentRole.unregChat(chat_id)

    ###ADMIN###
    def removeToken(self, chat_id):
        '''
        chat_id of owner
        '''
        self.currentRole.removeToken(chat_id)

    def tesaja(self):
        hasil = self.currentRole.tesaja()
        return hasil
        

