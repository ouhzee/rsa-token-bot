from abc import abstractclassmethod, ABC
from telegram import bot
import os, messageformat
from dbhelper import Database

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
        hasilparsing = messageformat.parsingGetOwner(hasilquery)
        return hasilparsing

    def reqToken(self, tokenid):
        '''
        Return passcode->str
        :param tokenid: chat_id of current user
        '''
        db = Database()
        db.connection()
        fetchtoken = db.getUser(tokenid=tokenid)
        if not fetchtoken:
            return False
        username = messageformat.parsingPasscode(fetchtoken)
        cmd = os.popen(f"stoken --rcfile=.{username}")
        passcode = cmd.read()
        return passcode

    def registerToken(self, chat_id: int, chat_name: str, username: str, setpin: int, team_name: int, token=None, sdtid=None):
        db = Database()
        db.connection()
        self.importToken(username, setpin, sdtid, token)
        db.insertOwner(chat_id, chat_name, team_name, username)
        return

    def importToken(self, username, setpin, sdtid, token):
        if sdtid == None:
            os.popen(f"stoken import --token={token} --new-password=''")
        else:
            os.popen(f"stoken import --file=sdtid/{username}.sdtid --new-password=''")
        os.popen(f"stoken setpin {setpin}")
        os.popen(f"mv $HOME/.stokenrc rcfile/.{username}")

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
        Please type / click one of the command below.
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
        Please type / click one of the command below.
        
/registertoken<code>  - register/import token to bot.</code>
/registerchat<code>   - register current chat.</code>
/listchat<code>       - display list of your approved chat.</code>
/unregtoken<code>     - unregister/delete your token.</code>
/unregchat<code>      - unregister your approved chat/group.</code>
        
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
        Please type / click one of the command below
        
/registertoken<code>  - Import token to bot.</code>
/registerchat<code>   - Register current chat/group.</code>
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

    def reqPasscode(self, chat_id):
        '''
        :param chat_id: chat_id of current user
        '''
        self.currentRole.reqPasscode(chat_id)

    def registerToken(self, chat_id: int, chat_name: str, username: str, setpin: int, team_id: int, token=None, sdtid=None):
        self.currentRole.registerToken()

    def registerChat(self, chat_id, chat_name, token):
        self.currentRole.registerChat(chat_id, chat_name, token)

    ###Owner###
    def listChat(self, chat_id):
        '''
        chat_id of owner
        '''
        self.currentRole.listChat(chat_id)

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
        

