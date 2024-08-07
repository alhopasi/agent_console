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
    
    def setSecret(self, secret):
        self.secrets.append(secret)
        secret.alliances.append(self)
        db.session.commit()
        return "Salaisuus " + str(secret.id) + " asetettu liitolle."
    
    def removeSecret(self, secret):
        self.secrets.remove(secret)
        db.session.commit()
        return "Salaisuus " + str(secret.id) + " poistettu liitolta."
    
    @staticmethod
    def getAlliance(allianceId):
        return Alliance.query.filter_by(id=allianceId).first()
    
    @staticmethod
    def listAlliancesForAdmin():
        alliances = Alliance.query.all()

        allianceNamesWidth = 4
        for a in alliances:
            if len(a.name) > allianceNamesWidth: allianceNamesWidth = len(a.name)

        response = "id | " + setEmptySpacesLeading("nimi", allianceNamesWidth) + " | salaisuudet"
        for a in alliances:
            response += "\n" + setEmptySpacesLeading(str(a.id), 2) + \
                        " | " + setEmptySpacesLeading(a.name, allianceNamesWidth) + \
                        " |"
            for s in a.secrets:
                response += " " + str(s.id)
        return response

    @staticmethod
    def createAlliance(name):
        db.session.add(Alliance(name))
        db.session.commit()
        return "Liitto luotu: " + name
    
    def delete(self):
        Alliance.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Liitto poistettu: " + str(self.id) + " | " + self.name