from sqlalchemy import event
from flask_login import UserMixin
from datetime import datetime
from agent_console import db
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


    def __init__(self, name, password, nation="", alliance="", role="player"):
        self.name = name.strip()
        self.password = password.strip()
        self.nation = nation.strip()
        self.currency = 5
        self.alliance = alliance
        self.role = role.strip()

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
        self.alliance = alliance

    def setRole(self, role):
        self.role = role.strip()

    def getInfo(self):
        playerInfo = "pelaaja:   " + self.name + \
              "\n" + "valtio:    " + self.nation + \
              "\n" + "rahat:     " + str(self.currency) + \
              "\n" + "liitto:    " + Alliance.getAlliance(self.alliance).name + \
              "\n" + "viestejä:  " + str(len(self.getMessages())) + \
              "\n" + "lukematta: " + str(self.getUnreadMessagesAmount())
        
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
            response += " | " + str(m.date_created)
        return response
    
    def messagesRead(self, messageNumber):
        messages = self.getMessages()
        if messages[int(messageNumber)].read == False:
            messages[int(messageNumber)].read = True
            db.session.commit()
        return messages[int(messageNumber)].message

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
            " | " + setEmptySpacesLeading("liitto", 8) + \
            " | " + " rooli"
        for u in users:
            response += "\n" + setEmptySpacesLeading(str(u.id), 2) + \
                        " | " + setEmptySpacesLeading(u.name, userColumnSizes[0]) + \
                        " | " + setEmptySpacesLeading(u.password, userColumnSizes[1]) + \
                        " | " + setEmptySpacesLeading(u.nation, userColumnSizes[2]) + \
                        " | " + setEmptySpacesLeading(str(u.currency), 2) + \
                        " | " + setEmptySpacesLeading(str(u.alliance), 8) + \
                        " | " + setEmptySpacesLeading(u.role, 5)
        return response
    
    @staticmethod
    def createUser(name, password, nation, alliance):
        if Alliance.query.filter_by(id=alliance).first() is not None:
            db.session.add(User(name, password, nation, alliance))
            db.session.commit()
            return "Käyttäjä luotu: " + name + " | " + password + " | " + nation + " | " + alliance
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
        return response + "Käyttäjä poistettu: " + str(self.id) + " | " + self.name + " | " + self.password + " | " + self.nation + " | " + str(self.currency) + " | " + str(self.alliance)
        

@event.listens_for(User.__table__, "after_create")
def createAdminUser(*args, **kwargs):
    db.session.add(User(name="admin", password="kissa123", role="admin"))
    db.session.commit()


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False) #viestin vastaanottajan numero
    message = db.Column(db.String(256), nullable=False) #viesti
    read = db.Column(db.Boolean, default=False) # kun luettu, set True
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, user_id, message):
        self.user_id = user_id.strip()
        self.message = message.strip()

    def setId(self, id):
        response = "Viestin vanha id: " + str(self.id)
        self.id = int(id.strip())
        db.session.commit()
        response += ", uusi id: " + str(self.id)
        return response
    
    def setPlayer(self, player_id):
        user = User.query.filter_by(id=player_id).first()
        if user is not None:
            if user.role != "player":
                return "Ei voida asettaa pelaajan id:tä, pelaajaa ei ole"
            response = "Viestin vanha pelaaja id: " + str(self.user_id)
            self.user_id=player_id.strip()
            db.session.commit()
            response += ", uusi pelaajan id: " + str(self.user_id)
            return response
        return "Ei voida asettaa pelaajan id:tä - pelaajaa ei ole"
    
    def setMessage(self, message):
        response = "Viestin vanha viesti: " + self.message
        self.message = message
        response += ", uusi viesti: " + self.message
        return response
    
    def setTimestamp(self, timestamp):
        format = "%Y-%m-%d %H:%M:%S"
        if datetime.strptime(timestamp, format):
            response = "Viestin vanha aikaleima: " + str(self.date_created)
            self.date_created = datetime.strptime(timestamp, format)
            db.session.commit()
            response += ", uusi aikaleima: " + str(self.date_created)
            return response
        return "Ei voida asettaa aikaleimaa - aikaleima on virheellinen"
    
    
    def setRead(self):
        response = "Viestin vanha luettu: " + str(self.read)
        if self.read == False: self.read = True
        else: self.read = False
        db.session.commit()
        response += ", uusi tila: " + str(self.read)
        return response
    
    @staticmethod
    def getMessage(messageId):
        message = Message.query.filter_by(id=messageId).first()
        return message
    
    @staticmethod
    def createMessage(playerId, message):
        if User.query.filter_by(id=playerId).first() is not None:
            db.session.add(Message(playerId, message))
            db.session.commit()
            return "Viesti luotu: " + playerId + " | " + message
        return "Ei voida luoda viestiä - pelaajaa ei löydy"
    
    def delete(self):
        Message.query.filter_by(id=self.id).delete()
        db.session().commit()
        return "Viesti poistettu: " + str(self.id) + " | " + str(self.user_id) + " | " + self.message + " | " + str(self.read) + " | " + str(self.date_created)

    
    @staticmethod
    def listMessagesForAdmin():
        messages = Message.query.all()
        messageLength = 6
        for m in messages:
            if len(m.message) > messageLength: messageLength = len(m.message)
        response = "id" + \
            " | " + "pelaajan id" + \
            " | " + setEmptySpacesLeading("viesti", messageLength) + \
            " | " + "luettu" + \
            " | " + "aikaleima"
        
        for m in messages:
            response += "\n" + setEmptySpacesLeading(str(m.id), 2) + \
                        " | " + setEmptySpacesLeading(str(m.user_id), 11) + \
                        " | " + setEmptySpacesLeading(m.message, messageLength) + \
                        " | " + setEmptySpacesLeading(str(m.read), 6) + \
                        " | " + str(m.date_created)
        return response

class Alliance(db.Model):
    __tablename__ = "alliances"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False, unique=True) #liittouman nimi

    def __init__(self, name):
        self.name = name.strip()

    def setId(self, id):
        response = "Liiton vanha id: " + str(self.id)
        self.id = int(id.strip())
        db.session.commit()
        response += ", uusi id: " + str(self.id)
        return response

    def setName(self, name):
        response = "Liiton vanha nimi: " + self.name
        self.name = name.strip()
        db.session.commit()
        response += ", uusi nimi: " + self.name
        return response
    
    @staticmethod
    def getAlliance(allianceId):
        return Alliance.query.filter_by(id=allianceId).first()
    
    @staticmethod
    def listAlliancesForAdmin():
        response = "id | nimi"
        alliances = Alliance.query.all()
        for a in alliances:
            response += "\n" + setEmptySpacesLeading(str(a.id), 2) + \
                        " | " + a.name
        return response

    @staticmethod
    def createAlliance(name):
        db.session.add(Alliance(name))
        db.session.commit()
        return "Liitto luotu: " + name
    
    def delete(self):
        if User.query.filter_by(alliance=self.id).first() is not None:
            return "Ei voida poistaa liittoa - Liitto on käytössä pelaajalla"
        Alliance.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Liitto poistettu: " + str(self.id) + " | " + self.name

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False, unique=True) # tehtävän nimi
    reward = db.Column(db.Integer, nullable=False) # palkintona rahaa
    secret = db.Column(db.String(256), nullable=False, unique=True) # salasana, jolla suoritetaan
    done = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True) # kun pelaaja tehnyt, pelaajan id tähän
    description = db.Column(db.String(256), nullable=False) # ohjeet suoritukseen

    def __init__(self, name, reward, secret, description):
        self.name = name.strip()
        self.reward = reward.strip()
        self.secret = secret.strip()
        self.description = description.strip()
        self.done = ""

    def setId(self, id):
        response = "Tehtävän vanha id: " + str(self.id)
        self.id = int(id.strip())
        db.session.commit()
        response += ", uusi id: " + str(self.id)
        return response

    def setName(self, name):
        response = "Tehtävän vanha nimi: " + self.name
        self.name = name.strip()
        db.session.commit()
        response += ", uusi nimi: " + self.name
        return response
    
    def setReward(self, reward):
        response = "Tehtävän vanha palkinto: " + str(self.reward)
        self.reward = reward.strip()
        db.session.commit()
        response += ", uusi palkinto: " + str(self.reward)
        return response
    
    def setSecret(self, secret):
        response = "Tehtävän vanha salaisuus: " + self.secret
        self.secret = secret.strip()
        db.session.commit()
        response += ", uusi salaisuus: " + self.secret
        return response

    def setDescription(self, desc):
        response = "Tehtävän vanha kuvaus: " + self.description
        self.description = desc.strip()
        db.session.commit()
        response += ", uusi kuvaus: " + self.description
        return response
    
    def setClaim(self, userId):
        if User.getUser(userId) is not None:
            response = "Tehtävän vanha tekijä: " + str(self.done)
            self.done = userId.strip()
            db.session.commit()
            response += ", uusi tekijä: " + str(self.done)
            return response
        return "Ei voida asettaa tekijää - Pelaajaa ei löydy"
    
    @staticmethod
    def claim(secret, playerId):
        task = Task.query.filter_by(secret=secret, done="").first()
        if task is not None:
            user = User.getUser(playerId)
            user.currency += task.reward
            task.done = user.id
            db.session.commit()
            return "Tehtävä " + task.name + " suoritettu onnistuneesti! Ansaitsit " + str(task.reward) + " $"
        return "Salaisuutta ei löydy"

    def unclaim(self):
        response = "Tehtävän vanha tekijä: " + str(self.done)
        self.done = ""
        db.session.commit()
        response += ", uusi tekijä: " + str(self.done)
        return response
    
    @staticmethod
    def getTask(taskId):
        return Task.query.filter_by(id=taskId).first()

    @staticmethod
    def listTasksForAdmin():
        tasks = Task.query.all()
        taskColumnSizes = [0] * 5
        taskColumnSizes[0] = 2
        taskColumnSizes[1] = 4
        taskColumnSizes[2] = 2
        taskColumnSizes[3] = 10
        taskColumnSizes[4] = 6
        for t in tasks:
            if len(str(t.id)) > taskColumnSizes[0]: taskColumnSizes[0] = len(str(t.id))
            if len(t.name) > taskColumnSizes[1]: taskColumnSizes[1] = len(t.name)
            if len(str(t.reward)) > taskColumnSizes[2]: taskColumnSizes[2] = len(str(t.reward))
            if len(t.secret) > taskColumnSizes[3]: taskColumnSizes[3] = len(t.secret)
            if len(str(t.done)) > taskColumnSizes[4]: taskColumnSizes[4] = len(str(t.done))

        response = setEmptySpacesLeading("id", taskColumnSizes[0]) + \
            " | " + setEmptySpacesLeading("nimi", taskColumnSizes[1]) + \
            " | " + setEmptySpacesLeading("$", taskColumnSizes[2]) + \
            " | " + setEmptySpacesLeading("salaisuus", taskColumnSizes[3]) + \
            " | " + setEmptySpacesLeading("tekijä", taskColumnSizes[4]) + \
            " | " + "kuvaus"
        
        for t in tasks:
            response += "\n" + setEmptySpacesLeading(str(t.id), taskColumnSizes[0]) + \
                        " | " + setEmptySpacesLeading(t.name, taskColumnSizes[1]) + \
                        " | " + setEmptySpacesLeading(str(t.reward), taskColumnSizes[2]) + \
                        " | " + setEmptySpacesLeading(t.secret, taskColumnSizes[3]) + \
                        " | " + setEmptySpacesLeading(str(t.done), taskColumnSizes[4]) + \
                        " | " + t.description
        return response

    @staticmethod
    def listTasks():
        def sortByName(t):
            return t.name

        tasks = Task.query.filter_by().all()
        taskNameLength = 7
        taskRewardLength = 2

        for t in tasks:
            if taskNameLength < len(t.name): taskNameLength = len(t.name)
            if taskRewardLength < len(str(t.reward)): taskRewardLength = len(str(t.reward))

        tasks = Task.query.filter_by(done="").all()
        tasks.sort(key=sortByName)

        response = setEmptySpacesLeading("tehtävä", taskNameLength) + " | " + setEmptySpacesLeading("$", taskRewardLength) + " | kuvaus"
        for t in tasks:
            response += "\n" + setEmptySpacesLeading(t.name, taskNameLength) + " | " + setEmptySpacesLeading(str(t.reward), taskRewardLength) + " | " + t.description

        tasks = Task.query.filter(Task.done != "").all()
        tasks.sort(key=sortByName)
        if len(tasks) > 0:
            response += "\n" + \
                        "\n" + "suoritetut tehtävät (ei voi suorittaa enää):"
            for t in tasks:
                response += "\n" + setEmptySpacesLeading(t.name, taskNameLength) + " | " + setEmptySpacesLeading(str(t.reward), taskRewardLength) + " | " + t.description

        return response
    
    @staticmethod
    def createTask(name,reward,secret,description):
        db.session.add(Task(name,reward,secret,description))
        db.session.commit()
        return "Tehtävä luotu: " + name + " | " + reward + " | " + secret + " | " + description
    
    def delete(self):
        Task.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Tehtävä poistettu: " + str(self.id) + " | " + self.name + " | " + str(self.reward) + " | " + self.secret + " | " + str(self.done) + " | " + self.description
