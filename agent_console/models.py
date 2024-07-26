from sqlalchemy import event
from flask_login import UserMixin
from agent_console import db
from agent_console.utils import setEmptySpacesLeading

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
        playerInfo = "pelaaja: " + self.name + \
              "\n" + "valtio:  " + self.nation + \
              "\n" + "rahat:   " + str(self.currency) + \
              "\n" + "liitto:  " + Alliance.getAlliance(self.alliance).name
        # viestien määrä
        # lukemattomien viestien määrä
        return playerInfo

    @staticmethod
    def getUser(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user
    
    @staticmethod
    def listUsers():
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
        
        # poista saapuneet viestit
        # poista "done" tehdyistä tehtävistä
        User.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Käyttäjä poistettu: " + str(self.id) + " | " + self.name + " | " + self.password + " | " + self.nation + " | " + str(self.currency) + " | " + str(self.alliance)
        

@event.listens_for(User.__table__, "after_create")
def createAdminUser(*args, **kwargs):
    db.session.add(User(name="admin", password="kissa123", role="admin"))
    db.session.commit()


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False) #viestin vastaanottajan numero
    message = db.Column(db.String(256), nullable=False) #viesti
    read = db.Column(db.Boolean, default=False) # kun luettu, set True

    def __init__(self, user_id, message):
        self.user_id = user_id
        self.message = message
    
    @staticmethod
    def getMessage(messageId):
        message = Message.query.filter_by(id=messageId).first()
        return message
    
    def delete(self):
        Message.query.filter_by(id=self.id).delete()
        db.session().commit()

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
        response += ", uusi nimi: " + str (self.name)
        return response
    
    @staticmethod
    def getAlliance(alliance_id):
        return Alliance.query.filter_by(id=alliance_id).first()
    
    @staticmethod
    def listAlliances():
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
    description = db.Column(db.String(256), nullable=False) # ohjeet suoritukseen
    reward = db.Column(db.Integer, nullable=False) # palkintona rahaa
    secret = db.Column(db.String(256), nullable=False, unique=True) # salasana, jolla suoritetaan
    done = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True) # kun pelaaja tehnyt, pelaajan id tähän

    def __init__(self, name, description, secret, reward=5):
        self.name = name
        self.description = description
        self.reward = reward
        self.secret = secret

    def claim(self, userId):
        self.claimed = userId

    def unclaim(self):
        self.claimed = ""

    def setName(self, name):
        self.name = name
    
    def setDescription(self, desc):
        self.description = desc
    
    def setReward(self, reward):
        self.reward = reward
    
    def setSecret(self, secret):
        self.secret = secret

