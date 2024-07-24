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
    
    def setName(self, name):
        self.name = name.strip()
    
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
        users = User.query.all()
        userColumnSizes = [0] * 3
        userColumnSizes[2] = 6
        for u in users:
            if userColumnSizes[0] < len(u.name): userColumnSizes[0] = len(u.name)
            if userColumnSizes[1] < len(u.password): userColumnSizes[1] = len(u.password)
            if userColumnSizes[2] < len(u.nation): userColumnSizes[2] = len(u.nation)
        response = "id" + \
            " | " + setEmptySpacesLeading("name", userColumnSizes[0]) + \
            " | " + setEmptySpacesLeading("password", userColumnSizes[1]) + \
            " | " + setEmptySpacesLeading("nation", userColumnSizes[2]) + \
            " | " + setEmptySpacesLeading("$", 2) + \
            " | " + setEmptySpacesLeading("alliance", 8) + \
            " | " + " role"
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
            return "User created: " + name + " | " + password + " | " + nation + " | " + alliance
        return "Can not create user - no alliance found"
    
    def delete(self):
        user = User.query.filter_by(id=self.id).first()
        if user.role == "player":
            User.query.filter_by(id=self.id).delete()
            db.session.commit()
            return "User deleted: " + str(self.id) + " | " + self.name + " | " + self.password + " | " + self.nation + " | " + str(self.currency) + " | " + str(self.alliance)
        return "Can not delete admin user"
        

@event.listens_for(User.__table__, "after_create")
def createAdminUser(*args, **kwargs):
    db.session.add(User(name="admin", password="kissa123", role="admin"))
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
            response += "\n" + setEmptySpacesLeading(str(a.id), 2) + \
                        " | " + a.name
        return response

    @staticmethod
    def createAlliance(name):
        db.session.add(Alliance(name))
        db.session.commit()
        return "Alliance created: " + name
    
    def delete(self):
        if User.query.filter_by(alliance=self.id).first() is not None:
            return "Can not delete alliance - Alliance is assigned to a player"
        Alliance.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Alliance deleted: " + str(self.id) + " | " + self.name
