import sqlite3


class Database:
    
    def __init__(self):
        self.connect = None
        self.dbFile = "rsatoken.db"

    def connection(self):
        try:
            conn = sqlite3.connect(self.dbFile)
            conn.execute("PRAGMA foreign_keys = 1")
            self.connect = conn
        except sqlite3.Error as err:
            print(err)

    def getTeam(self, team_name):
        """
        Check if team_name exists
        """
        query = '''select team_name from "team" where team_name = ?'''
        cur = self.connect.cursor()
        cur.execute(query, (team_name,))

        return cur.fetchall()


    def insertTeam(self, team_name, team_desc):
        """
        Create a new group/department into group table
        return:
         1 if success
         0 found duplicate team_name
        """
        try:
            query = '''insert into "team"(team_name, team_desc) values(?, ?)'''

            cur = self.connect.cursor()
            cur.execute(query, (team_name, team_desc))
            self.connect.commit()
            return 1
        except sqlite3.IntegrityError:
            return 0


    def insertOwner(self, chat_id, chat_name, team_name, token):
        """
        :param chat_id:
        :param chat_name:
        :param team_name:
        :param token:
        """
        query = '''insert into "owner"(chat_id, chat_name, team_name, team_desc, token) values(?, ?, ?, (select "team_desc" from "team" where "team_name" = ?), ?)'''
        #insert into "owner"(chat_id, chat_name, team_name, team_desc, token) values(444, "rozi", "mosigma", (select "team_desc" from "team" where "team_name" = "mosigma"), 777)
        #check if team_name exist
        team_desc = team_name
        teamname = team_name.lower().replace(" ", "")
        check = self.getTeam(teamname)
        if not check:
            self.insertTeam(teamname, team_desc)

        cur = self.connect.cursor()
        cur.execute(query, (chat_id, chat_name, teamname, teamname, token))
        self.connect.commit()
        return

    def insertUser(self, chat_id, chat_name, to_owner):
        """
        :param chat_id:
        :param chat_name:
        :param to_owner:
        """
        query = '''insert into "user"(chat_id, chat_name, to_owner, token) select ?, ?, ?, p.token from "owner" p where p.chat_id = ?'''

        cur = self.connect.cursor()
        try:
            cur.execute(query, (chat_id, chat_name, to_owner, to_owner))
            print(f"insertuser ini to_owner {to_owner}")
            self.connect.commit()
        except sqlite3.Error as e:
            print("insert uesr gagal ini error nya")
            print(e)
            return 1

    def updateTeam(self, team_name, team_desc):
        query = '''update "team" set team_name = ?,team_desc = ? where team_id = ?'''


    def updateOwner(self, **kwargs):
        """
        :param **kwargs: team_id/token, chat_id
        team_id if want to change team
        token if want to update token file

        """
        try:
            kwargs['team_name']
            query = '''update "owner" set "team_name" = ?, team_desc = (select "team".team_desc from "team" where "owner".team_name = "team".team_name) where chat_id = ?'''
            self.connect.execute(query, (kwargs.get('team_id'), kwargs.get('chat_id')))
            self.connect.commit()
        except KeyError:
            query = '''update "owner" set "token" = ? where chat_id = ?'''
            self.connect.execute(query, (kwargs.get('token'), kwargs.get('chat_id')))
            self.connect.commit()

    def updateUser(self, **kwargs):
        '''
        Description : update user table
        :param to_owner: chat_id of owner
        :param chat_id: chat_id of user
        '''
        query = '''update "user" set to_owner = ?, token = (select "owner".token from "owner" where "user".to_owner = "owner".chat_id) where chat_id = ?'''
        self.connect.execute(query, (kwargs.get('to_owner'), kwargs.ge('chat_id')))
        self.connect.commit()

    def delTeamOrOwner(self, **kwargs):
        '''
        delete record either
        pass either team_id or chat_id of owner
        '''
        try:
            kwargs['team_id']
            query = '''delete from "team" where team_name = ?'''
            self.connect.execute(query, (kwargs.get('team_name')))
            self.connect.commit()
        except KeyError:
            query ='''delete from "owner" where chat_id = ?'''
            self.connect.execute(query, (kwargs.get('chat_id'),))
            self.connect.commit()

    def delUser(self, chat_id):
        query = '''delete from "user" where chat_id = ?'''
        self.connect.ececute(query, (chat_id,))
        return

    def getUser(self, **kwargs):
        '''
        Return fetchall() set [(12, 'nama chat')]
        chat_id of owner to get list of user
        tokenid = chat_id of user to get passcode
        '''
        cur = self.connect.cursor()
        try:
            kwargs['tokenid']
            query = '''select token from "user" where chat_id = ?'''
            cur.execute(query, (kwargs.get('tokenid'),))
        except:
            query = '''select token, chat_id, chat_name from "user" where to_owner = ?'''
            cur.execute(query, (kwargs.get('chat_id'),))
        return cur.fetchall()

    def getOwner(self, **kwargs):
        '''
        :param kwargs: chat_id
        '''
        cur = self.connect.cursor()
        try:
            kwargs['chat_id']
            query = '''select chat_id from "owner" where chat_id = ?'''
            cur.execute(query, (kwargs.get('chat_id'),))
            
        except KeyError:
            cur.execute('''select token, chat_name, team_desc from "owner"''')
        return cur.fetchall()

    def getAdmin(self, chat_id):
        cur = self.connect.cursor()
        cur.execute('''select chat_id from "admin" where chat_id = ?''', (chat_id,))
        return cur.fetchall()

    def tesquery(self):
        cur = self.connect.cursor()
        cur.execute('''select * from "admin"''')
        return cur.fetchall()

    def getOwnerChatid(self, token):
        cur = self.connect.cursor()
        query = '''select chat_id, chat_name from "owner" where token = ?'''
        cur.execute(query, (token,))
        hasilquery = cur.fetchall()
        #convert into list
        hasil = [i for y in hasilquery for i in y]
        return hasil