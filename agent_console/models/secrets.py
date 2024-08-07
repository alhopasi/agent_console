from agent_console import db
from agent_console.models.alliance import alliance_secret_association
from agent_console.utils import setEmptySpacesLeading


class Secret(db.Model):
    __tablename__ = "secrets"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    tier = db.Column(db.Integer, nullable=False) # tier - arvontaan vaikuttava arvo. Pienet tierit ekana.
    secret = db.Column(db.String(256), nullable=False) #salaisuus
    alliances = db.relationship("Alliance", secondary=alliance_secret_association, back_populates="secrets")

    def __init__(self, tier, secret):
        self.tier = tier.strip()
        self.secret = secret.strip()

    def setId(self, id):
        response = "Salaisuuden vanha id: " + str(self.id)
        self.id = int(id.strip())
        db.session.commit()
        response += ", uusi id: " + str(self.id)
        return response

    def setTier(self, tier):
        response = "Salaisuuden vanha taso: " + str(self.tier)
        self.tier = int(tier.strip())
        db.session.commit()
        response += ", uusi taso: " + str(self.tier)
        return response

    def setSecret(self, secret):
        response = "Salaisuuden vanha salaisuus: " + self.secret
        self.secret = secret.strip()
        db.session.commit()
        response += ", uusi salaisuus: " + self.secret
        return response

    @staticmethod
    def listSecretsForAdmin():
        response = "id | taso | nimi"
        secrets = Secret.query.all()
        for s in secrets:
            response += "\n" + setEmptySpacesLeading(str(s.id), 2) + \
                        " | " + setEmptySpacesLeading(str(s.tier), 4) + \
                        " | " + s.secret
        return response

    @staticmethod
    def getSecret(secretId):
        return Secret.query.filter_by(id=secretId).first()

    @staticmethod
    def createSecret(tier, secret):
        db.session.add(Secret(tier, secret))
        db.session.commit()
        return "Salaisuus luotu: " + tier + " | " + secret

    def delete(self):
        Secret.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Salaisuus poistettu: " + str(self.id) + " | " + str(self.tier) + " | " + self.secret