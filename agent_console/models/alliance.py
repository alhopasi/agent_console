from agent_console import db
from agent_console.utils import setEmptySpacesLeading

alliance_secret_association = db.Table("alliances_secrets",
    db.Column("alliance_id", db.Integer, db.ForeignKey("alliances.id")),
    db.Column("secret_id", db.Integer, db.ForeignKey("secrets.id"))
)

class Alliance(db.Model):
    __tablename__ = "alliances"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False, unique=True)
    secrets = db.relationship("Secret", secondary=alliance_secret_association, back_populates="alliances")
    #secrets = db.relationship("Secret", secondary=alliance_secret_association, lazy="subquery", backref=db.backref("alliances", lazy=True), foreign_keys = "")

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
#        if User.query.filter_by(alliance=self.id).first() is not None:
#            return "Ei voida poistaa liittoa - Liitto on käytössä pelaajalla"
        Alliance.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Liitto poistettu: " + str(self.id) + " | " + self.name