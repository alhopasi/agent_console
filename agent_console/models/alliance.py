from agent_console import db
from agent_console.utils import setEmptySpacesLeading
from sqlalchemy.sql import text

alliance_secret_association = db.Table("alliances_secrets",
    db.Column("alliance_id", db.Integer, db.ForeignKey("alliances.id")),
    db.Column("secret_id", db.Integer, db.ForeignKey("secrets.id"))
)

alliance_win_table = db.Table("allianceWinTable",
    db.Column("sourceAlliance_id", db.Integer, db.ForeignKey("alliances.id")),
    db.Column("targetAlliance_id", db.Integer, db.ForeignKey("alliances.id"))
)

alliance_challenge_table = db.Table("allianceChallengeTable",
    db.Column("sourceAlliance_id", db.Integer, db.ForeignKey("alliances.id")),
    db.Column("challenge_id", db.Integer, db.ForeignKey("challenges.id")),
    db.Column("doneBy", db.Integer, db.ForeignKey("users.id"), nullable=True)
)

class Alliance(db.Model):
    __tablename__ = "alliances"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False, unique=True)
    secrets = db.relationship("Secret", secondary=alliance_secret_association, back_populates="alliances")
    winInstruction = db.Column(db.String(256))
    toWinAlliances = db.relationship("Alliance", secondary=alliance_win_table, back_populates="toLoseAlliances", primaryjoin=id == alliance_win_table.c.targetAlliance_id, secondaryjoin=id == alliance_win_table.c.sourceAlliance_id)
    toLoseAlliances = db.relationship("Alliance", secondary=alliance_win_table, back_populates="toWinAlliances", primaryjoin=id == alliance_win_table.c.sourceAlliance_id, secondaryjoin=id == alliance_win_table.c.targetAlliance_id)
    challengesCompleted = db.relationship("Challenge", secondary=alliance_challenge_table, back_populates="allianceHasCompleted")

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

    def setChallengeDone(self, challenge, user):
        self.challengesCompleted.append(challenge)
        challenge.allianceHasCompleted.append(self)
        db.session.commit()

        stmt = text("UPDATE allianceChallengeTable"
                    " SET doneBy = :user_id"
                    " WHERE sourceAlliance_id = :alliance_id AND challenge_id = :challenge_id").params(user_id=user.id, alliance_id=self.id, challenge_id=challenge.id)
        with db.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

        return "Haaste " + str(challenge.id) + " asetettu suoritetuksi liitolle - suorittaja: " + str(user.id)
    
    def removeChallengeDone(self, challenge):
        self.challengesCompleted.remove(challenge)
        db.session.commit()
        return "Haaste " + str(challenge.id) + " poistettu liitolta"
    
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
        challengesWidth = 8
        for a in alliances:
            if len(a.secrets)*2 > secretsWidth: secretsWidth = len(a.secrets)*2
            if len(a.name) > allianceNamesWidth: allianceNamesWidth = len(a.name)
            if len(a.toWinAlliances)*2 > alliancesToWinWidth: alliancesToWinWidth = len(a.toWinAlliances)*2
            if len(a.challengesCompleted)*2 > challengesWidth: challengesWidth = len(a.challengesCompleted)*2

        response = "id | " + setEmptySpacesLeading("nimi", allianceNamesWidth) + " | " + setEmptySpacesLeading("salaisuudet", secretsWidth) + " | " + setEmptySpacesLeading("haasteet", challengesWidth) + " | " + setEmptySpacesLeading("voita", alliancesToWinWidth) + " | " + "voitto-ohje"
        for a in alliances:
            response += "\n" + setEmptySpacesLeading(str(a.id), 2) + \
                        " | " + setEmptySpacesLeading(a.name, allianceNamesWidth) + \
                        " | "
            secretsList = ""
            for s in a.secrets:
                secretsList += setEmptySpacesLeading(str(s.id), 2)
            response += setEmptySpacesLeading(secretsList, secretsWidth) + \
                        " | "
            challengeList = ""
            for c in a.challengesCompleted:
                challengeList += setEmptySpacesLeading(str(c.id), 2)
            response += setEmptySpacesLeading(challengeList, challengesWidth) + \
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