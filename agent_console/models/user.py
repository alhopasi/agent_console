from sqlalchemy import event
from flask_login import UserMixin
from agent_console import db
from agent_console.models.alliance import Alliance
from agent_console.models.message import Message
from agent_console.models.task import Task
from agent_console.utils import setEmptySpacesLeading, setEmptySpacesTrailing


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False, unique=True) #pelaajan nimi
    password = db.Column(db.String(256), nullable=False, unique=True) #salalause, jolla kirjaudutaan
    nation = db.Column(db.String(256), nullable=True) #valtio
    currency = db.Column(db.Integer, nullable=True) #rahat
    alliance = db.Column(db.Integer, db.ForeignKey("alliances.id"), nullable=True)
    role = db.Column(db.String(256), nullable=False) #rooli - admin / player
    messages = db.relationship("Message", backref = "user")
    fakeAlliance = db.Column(db.Integer, db.ForeignKey("alliances.id"), nullable=True)


    def __init__(self, name, password, nation="", alliance="", fakeAlliance="", role="player"):
        self.name = name.strip()
        self.password = password.strip()
        self.nation = nation.strip()
        self.currency = 5
        self.alliance = alliance.strip()
        self.role = role.strip()
        self.fakeAlliance = fakeAlliance.strip()

    def setId(self, id):
        response = "Pelaajan vanha id: " + str(self.id)
        self.id = int(id.strip())
        db.session.commit()
        response += ", uusi id: " + str(self.id)
        return response
    
    def setName(self, name):
        response = "Pelaajan vanha nimi: " + self.name
        self.name = name.strip()
        db.session.commit()
        response += ", uusi nimi: " + self.name
        return response
    
    def setNation(self, nation):
        response = "Pelaajan vanha valtio: " + self.nation
        self.nation = nation.strip()
        db.session.commit()
        response += ", uusi valtio: " + self.nation
        return response

    def setPassword(self, password):
        response = "Pelaajan vanha salasana: " + self.password
        self.password = password.strip()
        db.session.commit()
        response += ", uusi salasana: " + self.password
        return response

    def setCurrency(self, currency):
        response = "Pelaajan vanhat rahat: " + str(self.currency)
        self.currency = int(currency.strip())
        db.session.commit()
        response += ", uudet rahat: " + str(self.currency)
        return response

    def setAlliance(self, alliance):
        response = "Pelaajan vanhat liitto: " + str(self.alliance)
        self.alliance = alliance.strip()
        db.session.commit()
        response += ", uusi liitto: " + str(self.alliance)
        return response

    def setFakeAlliance(self, alliance):
        response = "Pelaajan vanhat liitto: " + str(self.fakeAlliance)
        self.fakeAlliance = alliance.strip()
        db.session.commit()
        response += ", uusi liitto: " + str(self.fakeAlliance)
        return response

    def getInfo(self):
        playerInfo = "pelaaja:    " + self.name + \
              "\n" + "valtio:     " + self.nation + \
              "\n" + "rahat:      " + str(self.currency) + \
              "\n" + "liitto:     " + Alliance.getAlliance(self.alliance).name
        if self.fakeAlliance:
              playerInfo += \
              "\n" + "valeliitto: " + Alliance.getAlliance(self.fakeAlliance).name
        playerInfo += \
              "\n" + "viestejä:   " + str(len(self.getMessages())) + \
              "\n" + "lukematta:  " + str(self.getUnreadMessagesAmount())
        
        tasks = Task.query.filter_by(done=self.id).all()
        if len(tasks) > 0:
            taskNameColumn = 4
            for t in tasks:
                if taskNameColumn < len(t.name): taskNameColumn = len(t.name)
            playerInfo += "\n" + \
                "suoritetut tehtävät:"
        for t in tasks:
            playerInfo += "\n  " + setEmptySpacesLeading(t.name, taskNameColumn) + " | " + str(t.reward) + " $"

        return playerInfo
    
    def getUnreadMessagesAmount(self):
        messages = Message.query.filter_by(user_id=self.id, read=False).all()
        return len(messages)
    
    def getMessages(self):
        messages = Message.query.filter_by(user_id=self.id).all()
        messages.sort(key=lambda x: x.date_created)
        return messages
    
    def messagesList(self):
        messages = self.getMessages()
        response = setEmptySpacesLeading("#", 4) + " | lukematta | saapunut"
        for i, m in enumerate(messages):
            response += "\n" + setEmptySpacesLeading("[" + str(i) + "]", 4)
            if m.read == False: response += " | lukematta"
            else: response += " |          "
            response += " | " + m.date_created.strftime("%Y-%m-%d %H:%M:%S")
        return response
    
    def messagesRead(self, messageNumber):
        messages = self.getMessages()
        if messages[int(messageNumber)].read == False:
            messages[int(messageNumber)].read = True
            db.session.commit()
        return messages[int(messageNumber)].message
    
    def tryClaimTask(self, secret):
        task = Task.query.filter_by(secret=secret, done="").first()
        if task:
            task.done = self.id
            self.currency += task.reward
            db.session.commit()
            return "Tehtävä " + task.name + " suoritettu onnistuneesti! Ansaitsit " + str(task.reward) + " $"
        return "Salaisuutta ei löydy"

    def sendMessage(self, message):
        db.session.add(Message(self.id, message))
        db.session.commit()
        return "Viesti lähetetty: " + self.id + " | " + message
    
    def claimTask(self, taskId):
        task = Task.query.filter_by(id=taskId).first()
        response = task.setClaim(self.id)
        return response

    @staticmethod
    def getUser(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user
    
    @staticmethod
    def getPlayersSortedByNation():
        def sortByNation(u):
            return u.nation
        
        users = User.query.filter_by(role="player").all()
        users.sort(key=sortByNation)
        return users
    
    @staticmethod
    def listPlayers():
        users = User.getPlayersSortedByNation()
        rows = 10
        if len(users) < rows:
            rows = len(users)

        nations = [""] * rows
        for i, u in enumerate(users):
            if i >= rows:
                nations[i % rows] += " | "
            nations[i % rows] += "[" + str(i) + "] " + setEmptySpacesTrailing(u.nation, 25)
        
        response = ""
        for row in nations:
            response += row + "\n"

        return response

    
    @staticmethod
    def listUsersForAdmin():
        users = User.query.all()
        userColumnSizes = [0] * 3
        userColumnSizes[0] = 4
        userColumnSizes[1] = 8
        userColumnSizes[2] = 6
        for u in users:
            if userColumnSizes[0] < len(u.name): userColumnSizes[0] = len(u.name)
            if userColumnSizes[1] < len(u.password): userColumnSizes[1] = len(u.password)
            if userColumnSizes[2] < len(u.nation): userColumnSizes[2] = len(u.nation)
        response = "id" + \
            " | " + setEmptySpacesLeading("nimi", userColumnSizes[0]) + \
            " | " + setEmptySpacesLeading("salasana", userColumnSizes[1]) + \
            " | " + setEmptySpacesLeading("valtio", userColumnSizes[2]) + \
            " | " + setEmptySpacesLeading("$", 2) + \
            " | " + setEmptySpacesLeading("liitto", 6) + \
            " | " + setEmptySpacesLeading("valeliitto", 10) + \
            " | " + "rooli"
        for u in users:
            response += "\n" + setEmptySpacesLeading(str(u.id), 2) + \
                        " | " + setEmptySpacesLeading(u.name, userColumnSizes[0]) + \
                        " | " + setEmptySpacesLeading(u.password, userColumnSizes[1]) + \
                        " | " + setEmptySpacesLeading(u.nation, userColumnSizes[2]) + \
                        " | " + setEmptySpacesLeading(str(u.currency), 2) + \
                        " | " + setEmptySpacesLeading(str(u.alliance), 6) + \
                        " | " + setEmptySpacesLeading(str(u.fakeAlliance), 10) + \
                        " | " + u.role
        return response
    
    @staticmethod
    def createUser(name, password, nation, alliance, fakeAlliance):
        if Alliance.query.filter_by(id=alliance).first() is not None:
            db.session.add(User(name, password, nation, alliance, fakeAlliance))
            db.session.commit()
            return "Käyttäjä luotu: " + name + " | " + password + " | " + nation + " | " + alliance + " | " + fakeAlliance
        return "Ei voida luoda käyttäjää - liittoa ei löydy"
    
    def delete(self):
        user = User.query.filter_by(id=self.id).first()
        if user.role == "admin":
            return "Admin käyttäjää ei voida poistaa"
        
        response = ""
        messages = Message.query.filter_by(user_id=self.id)
        for m in messages:
            response += m.delete() + "\n"

        tasks = Task.query.filter_by(done=self.id)
        for t in tasks:
            response += t.unclaim() + "\n"

        User.query.filter_by(id=self.id).delete()
        db.session.commit()
        return response + "Käyttäjä poistettu: " + str(self.id) + " | " + self.name + " | " + self.password + " | " + self.nation + " | " + str(self.currency) + " | " + str(self.alliance) + " | " + str(self.fakeAlliance)
        

@event.listens_for(User.__table__, "after_create")
def createAdminUser(*args, **kwargs):
    db.session.add(User(name="admin", password="kissa123", role="admin"))
    db.session.commit()
