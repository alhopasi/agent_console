from sqlalchemy import event
from flask_login import UserMixin
from agent_console import db
from agent_console.models.alliance import Alliance
from agent_console.models.message import Message
from agent_console.models.task import Task
from agent_console.models.secrets import Secret
from agent_console.utils import setEmptySpacesLeading, setEmptySpacesTrailing
import random, string, re

player_to_player_association = db.Table("playersTrueAllianceKnowledge",
    db.Column("sourcePlayer_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("targetPlayer_id", db.Integer, db.ForeignKey("users.id"))
)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(256), nullable=False, unique=True) #pelaajan nimi
    password = db.Column(db.String(256), nullable=False, unique=True) #salalause, jolla kirjaudutaan
    nation = db.Column(db.String(256), nullable=True) #valtio
    currency = db.Column(db.Integer, nullable=True) #rahat
    alliance = db.Column(db.Integer, db.ForeignKey("alliances.id"), nullable=True)
    role = db.Column(db.String(256), nullable=False) #rooli - admin / player
    messages = db.relationship("Message", backref = "user")
    fakeAlliance = db.Column(db.Integer, db.ForeignKey("alliances.id"), nullable=True)
    knownPlayers = db.relationship("User", secondary=player_to_player_association, back_populates="knownToPlayers", primaryjoin=id == player_to_player_association.c.targetPlayer_id, secondaryjoin=id == player_to_player_association.c.sourcePlayer_id)
    knownToPlayers = db.relationship("User", secondary=player_to_player_association, back_populates="knownPlayers", primaryjoin=id == player_to_player_association.c.sourcePlayer_id, secondaryjoin=id == player_to_player_association.c.targetPlayer_id)
    


    def __init__(self, name, password, nation="", alliance=None, fakeAlliance=None, role="player"):
        self.name = name.strip()
        self.password = password.strip()
        self.nation = nation.strip()
        self.currency = 5
        self.alliance = alliance
        self.role = role.strip()
        self.fakeAlliance = fakeAlliance

    def setId(self, id):
        response = "Pelaajan vanha id: " + str(self.id)
        self.id = int(id.strip())
        db.session.commit()
        response += ", uusi id: " + str(self.id)
        return response
    
    def setName(self, name):
        response = "Pelaajan vanha nimi: " + self.name
        self.name = name.strip()
        db.session.commit()
        response += ", uusi nimi: " + self.name
        return response
    
    def setNation(self, nation):
        response = "Pelaajan vanha valtio: " + self.nation
        self.nation = nation.strip()
        db.session.commit()
        response += ", uusi valtio: " + self.nation
        return response

    def setPassword(self, password):
        response = "Pelaajan vanha salasana: " + self.password
        self.password = password.strip()
        db.session.commit()
        response += ", uusi salasana: " + self.password
        return response

    def setCurrency(self, currency):
        response = "Pelaajan vanhat $: " + str(self.currency)
        self.currency = int(currency.strip())
        db.session.commit()
        response += ", uudet $: " + str(self.currency)
        return response

    def setAlliance(self, alliance):
        response = "Pelaajan vanha liitto: " + str(self.alliance)
        self.alliance = alliance.strip()
        db.session.commit()
        response += ", uusi liitto: " + str(self.alliance)
        return response

    def setFakeAlliance(self, alliance):
        response = "Pelaajan vanha valeliitto: " + str(self.fakeAlliance)
        self.fakeAlliance = alliance.strip()
        db.session.commit()
        response += ", uusi valeliitto: " + str(self.fakeAlliance)
        return response
    
    def setKnownPlayerAlliance(self, targetPlayer):
        self.knownPlayers.append(targetPlayer)
        self.knownToPlayers.append(self)
        db.session.commit()
        return "Tieto pelaajan " + str(targetPlayer.id) + " liitosta asetettu"
    
    def removeKnownPlayerAlliance(self, targetPlayer):
        self.knownPlayers.remove(targetPlayer)
        db.session.commit()
        return "Tieto pelaajan " + str(targetPlayer.id) + " liitosta poistettu"

    def getInfo(self):
        playerInfo = "pelaaja:    " + self.name + \
              "\n" + "valtio:     " + self.nation + \
              "\n" + "$:          " + str(self.currency) + \
              "\n" + "liitto:     " + Alliance.getAlliance(self.alliance).name
        if self.fakeAlliance != self.alliance:
              playerInfo += \
              "\n" + "valeliitto: " + Alliance.getAlliance(self.fakeAlliance).name
        playerInfo += \
              "\n" + "viestejä:   " + str(len(self.getMessages())) + \
              "\n" + "lukematta:  " + str(self.getUnreadMessagesAmount())
        
        tasks = Task.query.filter_by(done=self.id).all()
        if len(tasks) > 0:
            taskNameColumn = 4
            for t in tasks:
                if taskNameColumn < len(t.name): taskNameColumn = len(t.name)
            playerInfo += "\n" + "suoritetut tehtävät:"
        for t in tasks:
            playerInfo += "\n  " + setEmptySpacesLeading(t.name, taskNameColumn) + " | " + str(t.reward) + " $"

        secrets = Alliance.getAlliance(self.alliance).secrets
        if len(secrets) > 0:
            playerInfo += "\n" + "tiimin paljastetut salaisuudet:"
            for s in secrets:
                playerInfo += "\n  " + s.secret

        return playerInfo
    
    def getUnreadMessagesAmount(self):
        messages = Message.query.filter_by(user_id=self.id, read=False).all()
        return len(messages)
    
    def getMessages(self):
        messages = Message.query.filter_by(user_id=self.id).all()
        messages.sort(key=lambda x: x.date_created)
        return messages
    
    def messagesList(self):
        messages = self.getMessages()
        response = setEmptySpacesLeading("#", 4) + " | lukematta | saapunut"
        for i, m in enumerate(messages):
            response += "\n" + setEmptySpacesLeading("[" + str(i) + "]", 4)
            if m.read == False: response += " | lukematta"
            else: response += " |          "
            response += " | " + m.date_created.strftime("%Y-%m-%d %H:%M:%S")
        return response
    
    def messagesRead(self, messageNumber):
        messages = self.getMessages()
        if messages[int(messageNumber)].read == False:
            messages[int(messageNumber)].read = True
            db.session.commit()
        return messages[int(messageNumber)].message
    
    def tryClaimTask(self, code):
        task = Task.query.filter_by(code=code, done=None).first()
        if task:
            task.done = self.id
            self.currency += task.reward
            db.session.commit()
            return "Tehtävä " + task.name + " suoritettu onnistuneesti! Ansaitsit " + str(task.reward) + " $"
        return "Koodia ei löydy"
    
    def claimTask(self, taskId):
        task = Task.query.filter_by(id=taskId).first()
        response = task.setClaim(self.id)
        return response
    
    def transferCurrency(self, targetId, amount):
        if int(amount) < 0:
            return "Ahaa, yritit huijata vai? Ei onnistu."
        if int(amount) == "0":
            return "Et voi siirtää " + amount + "$"
        if self.currency >= int(amount):
            players = User.getPlayerList()
            if len(players) > int(targetId):
                if players[int(targetId)] == self:
                    return "Siirsit itsellesi " + amount + "$"
                self.currency -= int(amount)
                players[int(targetId)].currency += int(amount)
                db.session.commit()
                return "Siirretty " + amount + "$ valtiolle " + players[int(targetId)].nation
            else: return "Valtiota #" + targetId + " ei ole olemassa"
        else: return "Sinulla ei ole " + amount + "$"
    
    def revealAlliance(self, player):
        if player == self:
            return "Tiedät jo oman liittosi"
        if player in self.knownPlayers:
            return "Tiedät jo tämän pelaajan liiton."
        if self.currency < 3:
            return "Sinulla ei ole 3 $"
        self.knownPlayers.append(player)
        player.knownToPlayers.append(self)
        self.currency -= 3
        db.session.commit()
        return "Maksoit 3 $" + \
            "\n" + "Pelaaja " + player.nation + " kuuluu liitton " + Alliance.getAlliance(player.alliance).name
    
    def sendMessage(self, player, messageText):
        if player == self:
            return "Et voi lähettää itsellesi viestiä"
        if self.currency < 1:
            return "Sinulla ei ole 1 $"
        message = Message(player.id, messageText.strip())
        self.currency -= 1
        db.session.add(message)
        db.session.commit()
        return "Maksoit 1 $" + \
            "\n" + "Lähetit viestin valtiolle " + player.nation + ": " + messageText.strip()

    @staticmethod
    def getUser(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user
    
    @staticmethod
    def getPlayerList():
        def sortByFakeAlliance(p):
            return Alliance.getAlliance(p.fakeAlliance).name
        
        def sortByNation(p):
            return p.nation
        
        players = User.query.filter_by(role="player").all()
        players.sort(key=sortByNation)
        players.sort(key=sortByFakeAlliance)
        return players

    def getUserList(self):
        def sortByName(u):
            return u.name
        users = User.query.filter(User.role != "admin").all()
        users.remove(self)
        users.sort(key=sortByName)
        return users
    
    def printUserList(self):
        users = self.getUserList()
        response = ""

        rows = 5
        if len(users) < rows:
            rows = len(users)

        nameLength = 5
        for u in users:
            if len(u.name) > nameLength: nameLength = len(u.name)

        usersList = [""] * rows

        header = ""
        for i, u in enumerate(users):
                if i % rows == 0:
                    if i > 0: header += "   | "
                    header += setEmptySpacesLeading("#", 3) + "  " + setEmptySpacesTrailing("nimi", nameLength)
                if i >= rows:
                    usersList[i % rows] += "   | "
                usersList[i % rows] += setEmptySpacesLeading("[" + str(i),3) + "] " + setEmptySpacesTrailing(u.name, nameLength)

        response = header
        for row in usersList:
            response += "\n" + row
        return response
    
    def revealSecret(self):
        def sortBySecretTier(s):
            return s.tier

        if self.currency < 6:
            return "Sinulla ei ole 6 $"
        secrets = Secret.query.all()
        filtered_secrets = []
        a = Alliance.getAlliance(self.alliance)
        for s in secrets:
            if a not in s.alliances:
                filtered_secrets.append(s)

        if len(filtered_secrets) == 0:
            return "Liittosi tietää jo kaikki salaisuudet"

        random.shuffle(filtered_secrets)
        filtered_secrets.sort(key=sortBySecretTier)
        secret = filtered_secrets[0]
        a.secrets.append(secret)
        self.currency -= 6
        db.session.commit()
        return "Maksoit 6 $" + \
            "\n" + "Paljastit salaisuuden: " + secret.secret

    def printPlayerList(self):
        alliances = Alliance.query.all()
        fakeAllianceText = "Liitto"
        fakeAllianceNameLength = len(fakeAllianceText)
        
        for a in alliances:
            if len(a.name) > fakeAllianceNameLength: fakeAllianceNameLength = len(a.name)

        players = User.getPlayerList()
        
        rows = 5
        if len(players) < rows:
            rows = len(players)

        header = ""

        nations = [""] * rows

        if len(self.knownPlayers) == 0:
            for i, u in enumerate(players):
                if i % rows == 0:
                    header += setEmptySpacesLeading("#", 3) + "  | " + setEmptySpacesTrailing(fakeAllianceText, fakeAllianceNameLength) + " | " + setEmptySpacesTrailing("Valtio", 25)
                nations[i % rows] += setEmptySpacesLeading("[" + str(i), 3) + "] | " + setEmptySpacesTrailing(Alliance.getAlliance(u.fakeAlliance).name, fakeAllianceNameLength) + " | " + setEmptySpacesTrailing(u.nation, 25)
        else:
            allianceText = "Liitto"
            allianceNameLength = len(allianceText) if len(allianceText) > fakeAllianceNameLength else fakeAllianceNameLength
            fakeAllianceText = "Valeliitto"
            fakeAllianceNameLength = len(fakeAllianceText) if len(fakeAllianceText) > fakeAllianceNameLength else fakeAllianceNameLength
            for i, u in enumerate(players):
                if i % rows == 0:
                    header += setEmptySpacesLeading("#", 3) + " | " + setEmptySpacesTrailing(fakeAllianceText, fakeAllianceNameLength) + " | " + setEmptySpacesTrailing(allianceText, allianceNameLength) + " | " + setEmptySpacesTrailing("Valtio", 25)
                nations[i % rows] += setEmptySpacesLeading("[" + str(i), 3) + "] | " + setEmptySpacesTrailing(Alliance.getAlliance(u.fakeAlliance).name, fakeAllianceNameLength) + " | "
                if u in self.knownPlayers:
                    nations[i % rows] += setEmptySpacesTrailing(Alliance.getAlliance(u.alliance).name, allianceNameLength)
                else:
                    nations[i % rows] += setEmptySpacesTrailing("", allianceNameLength) 
                nations[i % rows] += " | " + setEmptySpacesTrailing(u.nation, 25)

        response = header
        for row in nations:
            response += "\n" + row

        return response

    def tryWin(self, userIdsToCheck):
        if not re.match("^(?:\d+ ?)+$", userIdsToCheck.strip()):
            return "Tarkasta komentosi - 'voita " + userIdsToCheck + "' ei ole oikeassa muodossa"
        userIdsToCheck = userIdsToCheck.strip().split(" ")
        userIdsToCheck = list(set(userIdsToCheck))  #remove duplicates
        users = self.getUserList()
        for u in userIdsToCheck:
            if len(users) <= int(u):
                return "Tarkasta komentosi - henkilöä " + u + " ei löydy henkilölistalta."
        
        if self.currency < 5:
            return "Sinulla ei ole 5 $"
        self.currency -= 5
        db.session.commit()
        
        toWinAlliances = Alliance.getAlliance(self.alliance).toWinAlliances

        winner = False
        winText = ""

        for a in toWinAlliances:
            allUsersInAlliance = True
            usersToFind = User.query.filter_by(alliance = a.id).all()
            for u in userIdsToCheck:
                user = users[int(u)]
                if user in usersToFind:
                    usersToFind.remove(user)
                else:
                    allUsersInAlliance = False
                    break
            if len(usersToFind) == 0 and allUsersInAlliance:
                winner = True
                winText = "  -- Voittaja on " + Alliance.getAlliance(self.alliance).name + "!  " + self.name + "(" + self.nation + ")" + " sai selville " + a.name + " liiton kaikki jäsenet! --"
                break
        
        if winner:
            return "game.end" + \
                "\n" + "game.end.text " + winText + \
                "\n" + "Onneksi olkoon, voitit pelin!"

        return "Maksoit 5 $" + \
            "\n" + "Hyvä yritys, mutta väärin meni"

        
    
    @staticmethod
    def listUsersForAdmin():
        users = User.query.all()
        userColumnSizes = [0] * 3
        userColumnSizes[0] = 4
        userColumnSizes[1] = 8
        userColumnSizes[2] = 6
        for u in users:
            if u.role != "npc":
                if userColumnSizes[0] < len(u.name): userColumnSizes[0] = len(u.name)
                if userColumnSizes[1] < len(u.password): userColumnSizes[1] = len(u.password)
                if userColumnSizes[2] < len(u.nation): userColumnSizes[2] = len(u.nation)
        response = [""] * 4
        response[0] = " id" + \
            " | " + setEmptySpacesLeading("nimi", userColumnSizes[0]) + \
            " | " + setEmptySpacesLeading("salasana", userColumnSizes[1]) + \
            " | " + setEmptySpacesLeading("valtio", userColumnSizes[2]) + \
            " | " + setEmptySpacesLeading("$", 2) + \
            " | " + setEmptySpacesLeading("liitto", 6) + \
            " | " + setEmptySpacesLeading("valeliitto", 10) + \
            " | " + setEmptySpacesLeading("rooli", 6) + \
            " | " + "tieto pelaajan liitosta"
        for u in users:
            if u.role == "player":
                response[2] += "\n" + setEmptySpacesLeading(str(u.id), 3) + \
                            " | " + setEmptySpacesLeading(u.name, userColumnSizes[0]) + \
                            " | " + setEmptySpacesLeading(u.password, userColumnSizes[1]) + \
                            " | " + setEmptySpacesLeading(u.nation, userColumnSizes[2]) + \
                            " | " + setEmptySpacesLeading(str(u.currency), 2) + \
                            " | " + setEmptySpacesLeading(str(u.alliance), 6) + \
                            " | " + setEmptySpacesLeading(str(u.fakeAlliance), 10) + \
                            " | " + setEmptySpacesLeading(str(u.role), 6) + \
                            " |"
                for p in u.knownPlayers:
                    response[2] += " " + str(p.id)
            elif u.role == "admin":
                response[1] += "\n" + setEmptySpacesLeading(str(u.id), 3) + \
                            " | " + setEmptySpacesLeading(u.name, userColumnSizes[0]) + \
                            " | " + setEmptySpacesLeading(u.password, userColumnSizes[1]) + \
                            " | " + setEmptySpacesLeading("", userColumnSizes[2]) + \
                            " | " + setEmptySpacesLeading("", 2) + \
                            " | " + setEmptySpacesLeading("", 6) + \
                            " | " + setEmptySpacesLeading("", 10) + \
                            " | " + setEmptySpacesLeading(str(u.role), 6) + \
                            " |"
            elif u.role == "npc":
                response[3] += "\n" + setEmptySpacesLeading(str(u.id), 3) + \
                            " | " + setEmptySpacesLeading(u.name, userColumnSizes[0]) + \
                            " | " + setEmptySpacesLeading("", userColumnSizes[1]) + \
                            " | " + setEmptySpacesLeading("", userColumnSizes[2]) + \
                            " | " + setEmptySpacesLeading("", 2) + \
                            " | " + setEmptySpacesLeading("", 6) + \
                            " | " + setEmptySpacesLeading("", 10) + \
                            " | " + setEmptySpacesLeading(str(u.role), 6) + \
                            " |"
        return ''.join(response[i] for i in range(len(response)))

    @staticmethod
    def createUser(name, password, nation, alliance, fakeAlliance):
        if Alliance.query.filter_by(id=alliance.strip()).first() is not None:
            db.session.add(User(name, password, nation, alliance.strip(), fakeAlliance.strip()))
            db.session.commit()
            return "Käyttäjä luotu: " + name + " | " + password + " | " + nation + " | " + alliance + " | " + fakeAlliance
        return "Ei voida luoda käyttäjää - liittoa ei löydy"
    
    def delete(self):
        user = User.query.filter_by(id=self.id).first()
        if user.role == "admin":
            return "Admin käyttäjää ei voida poistaa"
        
        response = ""
        messages = Message.query.filter_by(user_id=self.id)
        for m in messages:
            response += m.delete() + "\n"

        tasks = Task.query.filter_by(done=self.id)
        for t in tasks:
            response += t.unclaim() + "\n"

        User.query.filter_by(id=self.id).delete()
        db.session.commit()
        return response + "Käyttäjä poistettu: " + str(self.id) + " | " + self.name + " | " + self.password + " | " + self.nation + " | " + str(self.currency) + " | " + str(self.alliance) + " | " + str(self.fakeAlliance)

    @staticmethod
    def createNPC(name):
        password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(24))
        user = User(name, password, nation="", alliance=None, fakeAlliance=None, role="npc")
        db.session.add(user)
        db.session.commit()
        return "Uusi ei-pelaaja luotu: " + name

@event.listens_for(User.__table__, "after_create")
def createAdminUser(*args, **kwargs):
    db.session.add(User(name="admin", password="kissa123", role="admin"))
    db.session.commit()
