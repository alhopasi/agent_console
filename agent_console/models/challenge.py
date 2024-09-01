from agent_console import db
from agent_console.utils import setEmptySpacesLeading
from agent_console.models.user import player_challenge_table
import re


class Challenge(db.Model):
    __tablename__ = "challenges"
    id = db.Column(db.Integer, primary_key=True) # works as tier, 1st is first -> 
    code = db.Column(db.String(256), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    playerHasCompleted = db.relationship("User", secondary=player_challenge_table, back_populates="challengesCompleted")

    def __init__(self, code, description):
        self.code = code.strip()
        self.description = description.strip()

    def adminSetDescription(self, description):
        response = "vanha kuvaus: " + self.description
        self.description = description.strip()
        db.session.commit()
        response += ", uusi kuvaus: " + self.description
        return response

    def adminSetCode(self, code):
        response = "vanha koodi: " + self.code
        self.code = code.strip()
        db.session.commit()
        response += ", uusi koodi: " + self.code
        return response

    def adminSetId(self, id):
        response = "vanha id: " + str(self.id)
        self.id = int(id.strip())
        db.session.commit()
        response += ", uusi id: " + str(self.id)
        return response

    @staticmethod
    def adminListChallenges():
        challenges = Challenge.query.all()
        challengeCodeLength = 5
        challengeDoneLength = 7

        for c in challenges:
            if challengeCodeLength < len(c.code): challengeCodeLength = len(c.code)
            if challengeDoneLength < len(c.playerHasCompleted)*2: challengeDoneLength = len(c.playerHasCompleted)*2

        response = "id | " + setEmptySpacesLeading("koodi", challengeCodeLength) + " | " + setEmptySpacesLeading("tehneet", challengeDoneLength) + " | kuvaus"

        for c in challenges:
            response += "\n" + setEmptySpacesLeading(str(c.id), 2) + " | " + setEmptySpacesLeading(c.code, challengeCodeLength) + " | "
            playersCompleted = ""
            for u in c.playerHasCompleted:
                playersCompleted += setEmptySpacesLeading(str(u.id), 2)
            response += setEmptySpacesLeading(playersCompleted, challengeDoneLength) + " | " + c.description
        
        return response
    
    def delete(self):
        Challenge.query.filter_by(id=self.id).delete()
        db.session.commit()
        return "Haaste poistettu: " + str(self.id) + " | " + self.code + " | " + self.description

    @staticmethod
    def getChallenge(id):
        return Challenge.query.filter_by(id=id).first()
    
    @staticmethod
    def createChallenge(code, description):
        code = code.strip()
        description = description.strip()
        if not re.match("[a-zA-Z0-9äÄöÖ]{5,}", code):
            return "koodin pitää olla vähintään 5 kirjainta tai numeroa pitkä"
        db.session.add(Challenge(code, description))
        db.session.commit()
        return "Haaste luotu: " + code + " | " + description