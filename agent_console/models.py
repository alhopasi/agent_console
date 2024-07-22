from sqlalchemy import event
from flask_login import UserMixin
from agent_console import db

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    user = db.Column(db.String(256), nullable=False) #pelaajan nimi
    password = db.Column(db.String(256), nullable=False) #salalause, jolla kirjaudutaan
    nation = db.Column(db.String(256), nullable=True) #valtio
    currency = db.Column(db.Integer, nullable=True) #rahat
    alliance = db.Column(db.Integer, db.ForeignKey('alliances.id'), nullable=True)
    role = db.Column(db.String(256), nullable=False) #rooli - admin / user
    messages = db.relationship('Message', backref = 'user')


    def __init__(self, user, password, nation="", alliance="", role="user"):
        self.user = user
        self.password = password
        self.nation = nation
        self.currency = 0
        self.alliance = alliance
        self.role = role
    
    def set_user(self, user):
        self.user = user
    
    def set_nation(self, nation):
        self.nation = nation

    def set_password(self, password):
        self.password = password

    def set_currency(self, currency):
        self.currency = currency

    def set_alliance(self, alliance):
        self.alliance = alliance

    def set_role(self, role):
        self.role = role

    @staticmethod
    def get_user(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user
    
    @staticmethod
    def list_users():
        User.query

@event.listens_for(User.__table__, "after_create")
def create_admin_user(*args, **kwargs):
    db.session.add(User(user="admin", password="kissa123", role="admin"))
    db.session.commit()


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) #viestin vastaanottajan numero
    message = db.Column(db.String(256), nullable=False) #viesti

    def __init__(self, user_id, message):
        self.user_id = user_id
        self.message = message
    
    @staticmethod
    def get_message(message_id):
        message = Message.query.filter_by(id=message_id).first()
        return message
    
    @staticmethod
    def delete_message(message_id):
        Message.get_message(message_id).delete()
        db.session().commit()

class Alliance(db.Model):
    __tablename__ = "alliances"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False) #liittouman nimi

    def __init__(self, name):
        self.name = name

    def change_name(self, name):
        self.name = name
    
    @staticmethod
    def get_alliance(alliance_id):
        alliance = Alliance.query.filter_by(id=alliance_id).first()
        return alliance
