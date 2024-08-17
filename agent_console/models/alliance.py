from agent_console import db
from agent_console.utils import setEmptySpacesLeading

alliance_secret_association = db.Table("alliances_secrets",
    db.Column("alliance_id", db.Integer, db.ForeignKey("alliances.id")),
    db.Column("secret_id", db.Integer, db.ForeignKey("secrets.id"))
)

alliance_win_table = db.Table("allianceWinTable",
    db.Column("sourceAlliance_id", db.Integer, db.ForeignKey("alliances.id")),
    db.Column("targetAlliance_id", db.Integer, db.ForeignKey("alliances.id"))
)

class Alliance(db.Model):
    __tablename__ = "alliances"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False, unique=True)
    secrets = db.relationship("Secret", secondary=alliance_secret_association, back_populates="alliances")
    winInstruction = db.Column(db.String(256))
    toWinAlliances = db.relationship("Alliance", secondary=alliance_win_table, back_populates="toLoseAlliances", primaryjoin=id == alliance_win_table.c.targetAlliance_id, secondaryjoin=id == alliance_win_table.c.sourceAlliance_id)
    toLoseAlliances = db.relationship("Alliance", secondary=alliance_win_table, back_populates="toWinAlliances", primaryjoin=id == alliance_win_table.c.sourceAlliance_id, secondaryjoin=id == alliance_win_table.c.targetAlliance_id)

    def __init__(self, name):
        self.name = name.strip()
        self.winInstruction = ""

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
    
    def setWinInstruction(self, winInstruction):
        self.winInstruction = winInstruction.strip()
        db.session.commit()
        return "Uusi voitto-ohje: " + self.winInstruction
    
    def setWinAlliance(self, alliance):
        toWinAlliance = Alliance.query.filter_by(id = alliance).first()
        self.toWinAlliances.append(toWinAlliance)
        toWinAlliance.toLoseAlliances.append(self)
        db.session.commit()
        return "Liitto voi voittaa nimeämällä pelaajat liitosta: " + str(toWinAlliance.id)
    
    def removeWinAlliance(self, alliance):
        self.toWinAlliances.remove(Alliance.query.filter_by(id = alliance).first())
        db.session.commit()
        return "Liitto " + alliance + " poistettu voittolistalta"
    
    @staticmethod
    def getAlliance(allianceId):
        return Alliance.query.filter_by(id=allianceId).first()
    
    @staticmethod
    def listAlliancesForAdmin():
        alliances = Alliance.query.all()

        allianceNamesWidth = 4
        secretsWidth = 11
        alliancesToWinWidth = 5
        for a in alliances:
            if len(a.secrets)*2 > secretsWidth: secretsWidth = len(a.secrets)*2
            if len(a.name) > allianceNamesWidth: allianceNamesWidth = len(a.name)
            if len(a.toWinAlliances)*2 > alliancesToWinWidth: alliancesToWinWidth = len(a.toWinAlliances)*2

        response = "id | " + setEmptySpacesLeading("nimi", allianceNamesWidth) + " | " + setEmptySpacesLeading("salaisuudet", secretsWidth) + " | " + setEmptySpacesLeading("voita", alliancesToWinWidth) + " | " + "voitto-ohje"
        for a in alliances:
            response += "\n" + setEmptySpacesLeading(str(a.id), 2) + \
                        " | " + setEmptySpacesLeading(a.name, allianceNamesWidth) + \
                        " | "
            secretsList = ""
            for s in a.secrets:
                secretsList += " " + str(s.id)
            response += setEmptySpacesLeading(secretsList, secretsWidth) + \
                        " | "
            alliancesToWinList = ""
            for aToWin in a.toWinAlliances:
                alliancesToWinList += " " + str(aToWin.id)
            response += setEmptySpacesLeading(alliancesToWinList, alliancesToWinWidth) + \
                        " | " + a.winInstruction
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