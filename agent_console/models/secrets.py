from agent_console import db


class Secret(db.Model):
    __tablename__ = "secrets"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    secret = db.Column(db.String(256), nullable=False) #viesti
