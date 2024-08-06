from agent_console import db
from agent_console.models.alliance import alliance_secret_association


class Secret(db.Model):
    __tablename__ = "secrets"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    secret = db.Column(db.String(256), nullable=False) #salaisuus
    alliances = db.relationship("Alliance", secondary=alliance_secret_association, back_populates="secrets")