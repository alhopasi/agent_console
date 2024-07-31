from datetime import datetime, timezone, timedelta
from agent_console import db
from agent_console.utils import setEmptySpacesLeading

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False) #viestin vastaanottajan numero
    message = db.Column(db.String(256), nullable=False) #viesti
    read = db.Column(db.Boolean, default=False) # kun luettu, set True
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(tz=timezone(timedelta(seconds=10800), 'EEST')))

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
        response = "Viestin vanha pelaaja id: " + str(self.user_id)
        self.user_id=player_id.strip()
        db.session.commit()
        response += ", uusi pelaajan id: " + str(self.user_id)
        return response

    
    def setMessage(self, message):
        response = "Viestin vanha viesti: " + self.message
        self.message = message
        response += ", uusi viesti: " + self.message
        return response
    
    def setTimestamp(self, timestamp):
        format = "%Y-%m-%d %H:%M:%S"
        if datetime.strptime(timestamp, format):
            response = "Viestin vanha aikaleima: " + self.date_created.strftime("%Y-%m-%d %H:%M:%S")
            self.date_created = datetime.strptime(timestamp, format)
            db.session.commit()
            response += ", uusi aikaleima: " + self.date_created.strftime("%Y-%m-%d %H:%M:%S")
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
        db.session.add(Message(playerId, message))
        db.session.commit()
        return "Viesti luotu: " + playerId + " | " + message

    
    def delete(self):
        Message.query.filter_by(id=self.id).delete()
        db.session().commit()
        return "Viesti poistettu: " + str(self.id) + " | " + str(self.user_id) + " | " + self.message + " | " + str(self.read) + " | " + self.date_created.strftime("%Y-%m-%d %H:%M:%S")

    
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
                        " | " + m.date_created.strftime("%Y-%m-%d %H:%M:%S")
        return response
