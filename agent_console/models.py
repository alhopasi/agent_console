from sqlalchemy import event
from flask_login import UserMixin
from agent_console import db

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    user = db.Column(db.String(256), nullable=False, unique=True) #pelaajan nimi
    password = db.Column(db.String(256), nullable=False, unique=True) #salalause, jolla kirjaudutaan
    nation = db.Column(db.String(256), nullable=True) #valtio
    currency = db.Column(db.Integer, nullable=True) #rahat
    alliance = db.Column(db.Integer, db.ForeignKey("alliances.id"), nullable=True)
    role = db.Column(db.String(256), nullable=False) #rooli - admin / user
    messages = db.relationship("Message", backref = "user")


    def __init__(self, user, password, nation="", alliance="", role="user"):
        self.user = user.strip()
        self.password = password.strip()
        self.nation = nation.strip()
        self.currency = 5
        self.alliance = alliance
        self.role = role.strip()
    
    def setUser(self, user):
        self.user = user.strip()
    
    def setNation(self, nation):
        self.nation = nation.strip()

    def setPassword(self, password):
        self.password = password.strip()

    def setCurrency(self, currency):
        self.currency = currency

    def setAlliance(self, alliance):
        self.alliance = alliance

    def setRole(self, role):
        self.role = role.strip()

    @staticmethod
    def getUser(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user
    
    @staticmethod
    def listUsers():
        User.query.all()

@event.listens_for(User.__table__, "after_create")
def createAdminUser(*args, **kwargs):
    db.session.add(User(user="admin", password="kissa123", role="admin"))
    db.session.commit()


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False) #viestin vastaanottajan numero
    message = db.Column(db.String(256), nullable=False) #viesti

    def __init__(self, user_id, message):
        self.user_id = user_id
        self.message = message
    
    @staticmethod
    def getMessage(messageId):
        message = Message.query.filter_by(id=messageId).first()
        return message
    
    @staticmethod
    def deleteMessage(messageId):
        Message.query.filter_by(id=messageId).first().delete()
        db.session().commit()

class Alliance(db.Model):
    __tablename__ = "alliances"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False, unique=True) #liittouman nimi

    def __init__(self, name):
        self.name = name.strip()

    def setId(self, id):
        response = "Alliance previous id: " + str(self.id)
        self.id = id
        db.session.commit()
        response += ", new id: " + str(self.id)
        return response

    def setName(self, name):
        response = "Alliance previous name: " + self.name
        self.name = name.strip()
        db.session.commit()
        response += ", new name: " + str (self.name)
        return response
    
    @staticmethod
    def getAlliance(alliance_id):
        return Alliance.query.filter_by(id=alliance_id).first()
    
    @staticmethod
    def listAlliances():
        response = "id | name"
        alliances = Alliance.query.all()
        for a in alliances:
            response += "\n"
            if a.id < 10: response += " "
            response += str(a.id) + " | " + a.name
        return response

    @staticmethod
    def createAlliance(name):
        db.session.add(Alliance(name))
        db.session.commit()
        return "Alliance created: " + name
    
    def delete(self):
        Alliance.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Alliance deleted: " + str(self.id) + " | " + self.name
