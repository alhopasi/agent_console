from flask_login import login_user, logout_user, current_user
import re
from agent_console.models.user import User
from agent_console.models.alliance import Alliance
from agent_console.models.message import Message
from agent_console.models.task import Task
from agent_console.models.secrets import Secret
from agent_console.models.challenge import Challenge
from agent_console.utils import setEmptySpacesLeading, setEmptySpacesTrailing
from datetime import datetime, timezone, timedelta
from agent_console import db

class GameState():
    startTime = "2024-09-15 14:45:00"
    #startTime = "2024-01-01 00:00:00"
    started = False
    finished = False
    infoText = "PELI KÄYNNISSÄ"
    firstChallenge = 0
    topChallenge = 0

    def updateChallengeInfo(self, challengeNumber, user):
        if self.topChallenge < challengeNumber:
            self.topChallenge = challengeNumber
            self.updateChallengeInfoText()
        if challengeNumber == 1:
            self.firstChallenge += 1
            self.updateChallengeInfoText()
            return "Salainen haaste suoritettu! Mene Haastevalikkoon [h]!" + \
                    "\n" + "Jos ratkaiset kaikki 10 haastetta, liittonne voittaa!"
        if challengeNumber == 10:
            self.finished = True
            self.infoText = "  -- Voittaja on " + Alliance.getAlliance(user.alliance).name + "!  " + user.name + " (" + user.nation + ")" + " suoritti 10 haastetehtävää! --"
            return "Onneksi olkoon, voitit pelin!"

        response = "Haaste suoritettu!" + \
        "\n" + "Seuraava haaste:"
        c = Challenge.query.filter_by(id=challengeNumber+1).first()
        if c == None: response += "\n" + "Seuraavaa haastetta ei löydy"
        else: response += "\n" + c.description
        return response
    
    def updateChallengeInfoText(self):
        if self.topChallenge > 0 and self.firstChallenge > 0:
            self.infoText = "Pelaajia, jotka avanneet salaisen haasteen: " + str(self.firstChallenge) + ". Suurin suoritettu haaste: " + str(self.topChallenge)
        else: self.infoText = "PELI KÄYNNISSÄ"

    def getInfo(self):
        if not self.started:
            startTime = datetime.strptime(self.startTime, "%Y-%m-%d %H:%M:%S")
            currentTime = datetime.strptime(getCurrentTime(), "%Y-%m-%d %H:%M:%S")
            relativeStartTime = startTime - currentTime
            if relativeStartTime > timedelta(0):
                if relativeStartTime.days > 0:
                    return "console.info   -- Pelin alkuun " + str(relativeStartTime.days) + " päivää --"
                hours = str(relativeStartTime.seconds // 3600)
                minutes = str(relativeStartTime.seconds // 60 % 60)
                seconds = str(relativeStartTime.seconds % 60)
                if len(hours) == 1: hours = "0" + hours
                if len(minutes) == 1: minutes = "0" + minutes
                if len(seconds) == 1: seconds = "0" + seconds
                return "console.info   -- Pelin alkuun " + hours + ":" + minutes + ":" + seconds + " --"
            else:
                self.started = True
        return "console.info " + getCurrentTime() + " | " + self.infoText
    
    def queryDBforChallengeInfo(self):
        self.topChallenge = 0
        self.firstChallenge = 0
        challenges = Challenge.query.all()
        for c in challenges:
            if len(c.playerHasCompleted) > 0:
                if c.id == 1 or c.id > self.topChallenge:
                    for u in c.playerHasCompleted:
                        self.updateChallengeInfo(c.id, u)

    def setFirstChallenge(self, challenge):
        self.firstChallenge = int(challenge)
        self.updateChallengeInfoText()
        return "haastetehtävän aloittaneita asetettu: " + str(challenge)
    
    def setTopChallenge(self, challenge):
        self.topChallenge = int(challenge)
        self.updateChallengeInfoText()
        return "suurin haaste asetettu: " + str(challenge)
    
    def getStatus(self):
        return "startTime: " + self.startTime + \
            "\n" + "started: " + str(self.started) + \
            "\n" + "finished: " + str(self.finished) + \
            "\n" + "infoText: " + self.infoText + \
            "\n" + "firstChallenge: " + str(self.firstChallenge) + \
            "\n" + "topChallenge: " + str(self.topChallenge)

game = GameState()



def parseMessage(msg):
    return re.match("^[a-zA-Z0-9äÄöÖåÅ\?\!,. :\-]*$", msg)

def getCurrentTime():
    return datetime.now(tz=timezone(timedelta(seconds=10800), 'EEST')).strftime("%Y-%m-%d %H:%M:%S")

def printTitle():
    title = '## ERITTÄIN SALAINEN OHJELMA ##'
    return title

def printCommands(path):
    commands = "[?] - komennot" + \
        "\n" + "[,] - tyhjennä ruutu"
    if not current_user.is_authenticated:
        commands += "\n" + "[salasana] - kirjaudu salasanalla"
    if current_user.is_authenticated:
        commands += "\n" + "[.] - päävalikkoon"
        if current_user.role == "player":
            commands += "\n" + "[i] - pelaajan info" + \
                        "\n" + "[p] - pelaajat / henkilöt" + \
                        "\n" + "[v] - valtiot"
        commands += "\n" + "[!] - kirjaudu ulos"

        if current_user.role == "player":
            commands += "\n"
            if path == "":
                commands += "\n" + "[s] - sähkeet" + \
                            "\n" + "[t] - tehtävät" + \
                            "\n" + "[a] - agenttitoiminnot"
                if len(current_user.challengesCompleted) > 0:
                    commands += "\n" + "[h] - haastetehtävä"
            if path == "sähkeet":
                commands += "\n" + "[s] - listaa sähkeet" + \
                            "\n" + "[#] - lue sähke #"
            if path == "tehtävät":
                commands += "\n" + "[t] - listaa tehtävät" + \
                            "\n" + "[koodi] - suorita tehtävä koodilla"
            if path == "agenttitoiminnot":
                commands += "\n" + setEmptySpacesLeading("$", 2) + " | " + setEmptySpacesTrailing("komento", 13) + " | kuvaus" + \
                            "\n" + setEmptySpacesLeading("0", 2)     + " | " + setEmptySpacesTrailing("[s # $]", 13) + " | siirrä $ rahaa valtiolle #" + \
                            "\n" + setEmptySpacesLeading("1", 2)     + " | " + setEmptySpacesTrailing("[k # viesti]", 13) + " | kirjoita sähke valtiolle #" + \
                            "\n" + setEmptySpacesLeading("5", 2)     + " | " + setEmptySpacesTrailing("[h #]", 13) + " | paljasta henkilön # valtio" + \
                            "\n" + setEmptySpacesLeading("2", 2)     + " | " + setEmptySpacesTrailing("[l #]", 13) + " | paljasta valtion # todellinen liitto" + \
                            "\n" + setEmptySpacesLeading("6", 2)     + " | " + setEmptySpacesTrailing("[salaisuus]", 13) + " | liitollesi paljastetaan salaisuus" + \
                            "\n" + setEmptySpacesLeading("0", 2)     + " | " + setEmptySpacesTrailing("[voita]", 13) + " | ohjeet voittamiseen" + \
                            "\n" + setEmptySpacesLeading("5", 2)     + " | " + setEmptySpacesTrailing("[voita # ...]", 13) + " | yritä voittoa liitollesi, ks. ohjeet!" + \
                            "\n" + \
                            "\n" + "Agenttitoiminnot maksavat $" + \
                            "\n" + "Varoitus! Toimintoja ei voi perua!"
            if path == "haaste":
                commands += "\n" + "Voita 10 haastetta ja voita peli liitollesi!" + \
                            "\n" + "Jokaisessa haasteessa pitää saada [koodi]" + \
                            "\n" + "Syötä koodi tällä haastesivulla!" + \
                            "\n" + \
                            "\n" + "[h] - listaa haasteet" + \
                            "\n" + "[koodi] - suorita haastetehtävä"

        if current_user.role == "admin":
            commands += "\n"
            if path == "":
                commands += "\n" + "[a] - admin-komennot"
            if path == "admin":
                commands += "\n" + "[l] - hallitse liittoja" + \
                            "\n" + "[p] - hallitse pelaajia" + \
                            "\n" + "[v] - hallitse viestejä" + \
                            "\n" + "[t] - hallitse tehtäviä" + \
                            "\n" + "[s] - hallitse salaisuuksia" + \
                            "\n" + "[h] - hallitse haasteita" + \
                            "\n" + "[peli] - hallitse peliä"
    return commands

def setGameStartTime(timestamp):
    format = "%Y-%m-%d %H:%M:%S"
    if datetime.strptime(timestamp, format):
        game.startTime = timestamp
        return "Aloitusaika asetettu " + timestamp

def toggleGameStart():
    game.started = not game.started
    if game.started: return "peli aloitettu"
    else: return "peli lopetettu"

def toggleGameFinished():
    game.finished = not game.finished
    if game.finished: return "peli voitettu"
    else: return "peli ei-voitettu"

def setGameInfoText(text):
    game.infoText = text
    return "infoteksti asetettu: " + text

def printAdminAllianceCommands():
    commands = "[ll] - liitot listaa" + \
        "\n" + "[lu liiton_nimi] - liitot uusi" + \
        "\n" + "[lp liiton_id] - liitot poista" + \
        "\n" + "[lai liiton_id,uusi_id] - liitot aseta id" + \
        "\n" + "[lan liiton_id,uusi_nimi] - liitot aseta nimi" + \
        "\n" + "[las liiton_id,salaisuuden_id] - liitot aseta salaisuus" + \
        "\n" + "[lps liiton_id,salaisuuden_id] - liitot poista salaisuus" + \
        "\n" + "[lavo liiton_id,voitto-ohje] - liitot aseta voittoon ohje" + \
        "\n" + "[lavl liiton_id,voitettavan_liiton_id] - liitot aseta voittoon liitto" + \
        "\n" + "[lpvl liiton_id] - liitot poista voittoon liitot"
    return commands

def printAdminGameCommands():
    commands = "[peli aloitettu] - vaihda aloitettu tila" +\
        "\n" + "[peli lopetettu] - vaihda lopetettu tila" + \
        "\n" + "[peli info infoteksti] - aseta infoteksti" + \
        "\n" + "[peli aloitus YYYY-MM-DD HH-MM-SS] - aseta pelin aloitusaika" + \
        "\n" + "[peli suurin,#] - aseta suurin suoritettu haaste" + \
        "\n" + "[peli haasteet,#] - aseta haastehtävän aloittaneiden #" + \
        "\n" + "[peli status] - näytä pelin tiedot"
    return commands

def printAdminUserCommands():
    commands = "[pl] - pelaajat listaa" + \
        "\n" + "[pu nimi,salasana,valtio,liitto,valeliitto] - pelaajat uusi" + \
        "\n" + "[puep nimi] - pelaajat uusi ei-pelaaja" + \
        "\n" + "[pp pelaajan_id] - pelaajat poista" + \
        "\n" + "[pai pelaajan_id,uusi_id] - pelaajat aseta id" + \
        "\n" + "[pan pelaajan_id,uusi_nimi] - pelaajat aseta nimi" + \
        "\n" + "[pas pelaajan_id,uusi_salasana] - pelaajat aseta salasana" + \
        "\n" + "[pav pelaajan_id,uusi_valtio] - pelaajat aseta valtio" + \
        "\n" + "[pal pelaajan_id,uusi_liitto] - pelaajat aseta liitto" + \
        "\n" + "[pavl pelaajan_id,uusi_liitto] - pelaajat aseta valeliitto" + \
        "\n" + "[par pelaajan_id,uudet_rahat] - pelaajat aseta rahat" + \
        "\n" + "[paht pelaajan_id,toisen_pelaajan_id] - pelaajat aseta tositieto henkilön valtiosta" + \
        "\n" + "[ppht pelaajan_id,toisen_pelaajan_id] - pelaajat poista tositieto henkilön valtiosta" + \
        "\n" + "[palt pelaajan_id,toisen_pelaajan_id] - pelaajat aseta tositieto pelaajan liitosta" + \
        "\n" + "[pplt pelaajan_id,toisen_pelaajan_id] - pelaajat poista tositieto pelaajan liitosta" + \
        "\n" + "[pah pelaajan_id,haasteen_id] - pelaajat aseta haaste suoritetuksi" + \
        "\n" + "[pph pelaajan_id,haasteen_id] - pelaajat poista haaste"
    return commands

def printAdminMessageCommands():
    commands = "[vl] - viestit listaa" + \
        "\n" + "[vu pelaajan_id,viesti] - viestit uusi" + \
        "\n" + "[vp viestin_id] - viestit poista" + \
        "\n" + "[vai viestin_id,uusi_id] - viestit aseta id" + \
        "\n" + "[vap viestin_id,uusi_pelaajan_id] - viestit aseta pelaaja" + \
        "\n" + "[vav viestin_id,uusi_viesti] - viestit aseta viesti" + \
        "\n" + "[vaa viestin_id,uusi_aikaleima] - viestit aseta aikaleima" + \
        "\n" + "[val viestin_id] - viestit aseta luetuksi/ei-luetuksi" + \
        "\n" + "[vu kaikki,viesti] - viestit uusi kaikille"
    return commands

def printAdminTaskCommands():
    commands = "[tl] - tehtävät listaa" + \
        "\n" + "[tu tehtävän_nimi,palkinto,koodi,kuvaus] - tehtävät uusi" + \
        "\n" + "[tp tehtävän_id] - tehtävät poista" + \
        "\n" + "[tai tehtävän_id,uusi_id] - tehtävät aseta id" + \
        "\n" + "[tan tehtävän_id,uusi_nimi] - tehtävät aseta nimi" + \
        "\n" + "[tap tehtävän_id,uusi_palkinto] - tehtävät aseta palkinto" + \
        "\n" + "[tas tehtävän_id,uusi_koodi] - tehtävät aseta koodi" + \
        "\n" + "[tak tehtävän_id,uusi_kuvaus] - tehtävät aseta kuvaus" + \
        "\n" + "[tat tehtävän_id,tekijä] - tehtävät aseta tekijä" + \
        "\n" + "[tpt tehtävän_id] - tehtävät poista tekijä"
    return commands

def printAdminSecretCommands():
    commands = "[sl] - salaisuudet listaa" + \
        "\n" + "[su taso,salaisuus] - salaisuudet uusi" + \
        "\n" + "[sp salaisuuden_id] - salaisuudet poista" + \
        "\n" + "[sai salaisuuden_id,uusi_id] - salaisuudet aseta id" + \
        "\n" + "[sat salaisuuden_id,taso] - salaisuudet aseta taso" + \
        "\n" + "[sas salaisuuden_id,salaisuus] - salaisuudet aseta salaisuus"
    return commands

def printAdminChallengeCommands():
    commands = "[hl] - haasteet listaa" + \
        "\n" + "[hu koodi,kuvaus] - haasteet uusi" + \
        "\n" + "[hp haasteen_id] - haasteet poista" + \
        "\n" + "[hai haasteen_id,uusi_id] - haasteet aseta id" + \
        "\n" + "[hako haasteen_id,uusi_koodi] - haasteet aseta koodi" + \
        "\n" + "[haku haasteen_id,uusi_kuvaus] - haasteet aseta kuvaus"
    return commands

def printWinInstructions():
    return current_user.printPlayerList() + \
        "\n\n" + current_user.printUserList() + \
        "\n\n" + Alliance.getAlliance(current_user.alliance).winInstruction + \
        "\n\n" + "komento: voita # # # ... (esim: voita 2 6 12 ... jne)"

def secretChallengeMessage(player, message):
    if player.currency < 1:
        return "Sinulla ei ole 1 $"
    challenges = Challenge.query.all()
    code = ""
    for c in challenges:
        if "bond" in c.description.lower():
            if len(player.challengesCompleted) == c.id - 1:
                code = c.code
    if code == "": return "007 ei vastaa - sähkettä ei lähetetty"
    messages = player.getMessages()
    for m in messages:
        if "Tässä Bond" in m.message:
            return "007 ei vastaa - sähkettä ei lähetetty"
    messageCorrect = False
    messageText = "Hei. Tässä Bond. Kiitos viestistä. Koodi on '" + code + "'"
    if message.strip() == "My name is Bond, James Bond":
        messageCorrect = True
        messageText="Hei. Tässä Bond. Kirjoitit kaiken oikein, joten saat palkinnoksi 2 $. Koodi on '" + code + "'"
    returnMessage = Message(player.id, messageText)
    player.currency += 1 if messageCorrect else -1
    db.session.add(returnMessage)
    db.session.commit()
    return "Maksoit 1 $" + \
        "\n" + "Lähetit sähkeen Britannian Tiedustelupalvelun mahtavimmalle agentille: " + message.strip()

def tryLogin(password):
    user = User.query.filter_by(password=password).first()
    if user:
        login_user(user)
        game.queryDBforChallengeInfo()
        if current_user.role == "player":
            unreadMessageAmount = current_user.getUnreadMessagesAmount()
            if unreadMessageAmount == 1:
                unreadMessageAmount = "\n" + "Sinulla on 1 lukematon sähke"
            elif unreadMessageAmount > 1:
                unreadMessageAmount = "\n" + "Sinulla on " + str(unreadMessageAmount) + " lukematonta sähkettä"
            else: unreadMessageAmount = ""
            return "Kirjautuminen onnistui. Tervetuloa " + current_user.nation + unreadMessageAmount + \
                "\n" + "console.changeUser " + current_user.nation
        else: return "Kirjautuminen onnistui. Tervetuloa " + current_user.name + \
                "\n" + "console.changeUser " + current_user.name
    else: return "Kirjautuminen epäonnistui"


def handleMessage(command, path):
    try:
        if command == "get_info":
            return game.getInfo()
        if not parseMessage(command): return "No cheating!"
        if not current_user.is_authenticated and path != "":
            return "console.resetPath" + "\n" + "console.clear" + "\n" + "console.logout" + "\n" + printTitle() + "\n\n" + "Sessio katkennut, kirjaudu uudelleen."

        if command == "": return "[?] - komennot"
        if command == ",": return "console.clear" + "\n" + printTitle()
        if command == ".": return "console.resetPath"
        if command == "?": return printCommands(path)
        if current_user.is_authenticated:
            if command == "!": logout_user(); return "console.resetPath" + "\n" + "console.clear" + "\n" + "console.logout" + "\n" + printTitle()

            if current_user.role == "player":
                if command == "v": return current_user.printPlayerList()
                if command == "p": return current_user.printUserList()
                if command == "i": return current_user.getInfo()
                if path == "" and command == "s": return "console.changePath sähkeet"
                if path == "" and command == "t": return "console.changePath tehtävät"
                if path == "" and command == "a": return "console.changePath agenttitoiminnot"
                if path == "" and command == "h" and len(current_user.challengesCompleted) > 0: return "console.changePath haaste"
                if not game.started or game.finished:
                        return "Peli ei ole käynnissä"
                if len(current_user.challengesCompleted) == 0 and re.match("[a-zA-Z0-9]{5,}", command):
                    if current_user.tryClaimChallenge(command) == "1":
                        return game.updateChallengeInfo(1, current_user)
                if path == "sähkeet":
                    if command == "v": return current_user.messagesList()
                    if re.match("\d+", command): return current_user.messagesRead(command)
                if path == "tehtävät":
                    if command == "t": return Task.listTasks()
                    if command: return current_user.tryClaimTask(command)
                if path == "agenttitoiminnot":
                    if re.match("s ", command): commands = command.split(" "); return current_user.transferCurrency(commands[1], commands[2])
                    if re.match("h ", command): commands = command.split(" "); return current_user.revealUser(current_user.getUserList()[int(commands[1])])
                    if re.match("l ", command): commands = command.split(" "); return current_user.revealAlliance(User.getPlayerList()[int(commands[1])])
                    if re.match("k ", command):
                        commands = command.split(" ", 2)
                        if commands[1] == "007": return secretChallengeMessage(current_user, commands[2])
                        else: return current_user.sendMessage(User.getPlayerList()[int(commands[1])], commands[2])
                    if command == "salaisuus": return current_user.revealSecret()
                    if command == "voita": return printWinInstructions()
                    if re.match("voita ", command):
                        commands = command.split(" ", 1)
                        response = current_user.tryWin(commands[1])
                        if re.match("game\.end", response):
                            lines = response.splitlines()
                            for line in lines:
                                if line == "game.end": game.finished = True
                                elif re.match("game.info.text ", line): game.infoText = line.split("game.info.text ", 1)[1]
                                else: response = line
                        return response
                if path == "haaste":
                    if command == "h": return current_user.listChallenges()
                    if re.match("[a-zA-Z0-9äÄöÖ]{5,}", command):
                        response =  current_user.tryClaimChallenge(command)
                        if re.match("^\d+$", response):
                            return game.updateChallengeInfo(int(response), current_user)
                        else: return response
            if current_user.role == "admin":
                if path == "" and command == "a": return "console.changePath admin"
                if path == "admin":
                    if command == "l": return printAdminAllianceCommands()
                    if command == "ll": return Alliance.listAlliancesForAdmin()
                    if re.match("lu ", command): return Alliance.createAlliance(command.split(" ", 1)[1])
                    if re.match("lp ", command): return Alliance.getAlliance(command.split(" ", 1)[1]).delete()
                    if re.match("lai ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setId(commands[1])
                    if re.match("lan ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setName(commands[1])
                    if re.match("las ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setSecret(Secret.getSecret(commands[1]))
                    if re.match("lps ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).removeSecret(Secret.getSecret(commands[1]))
                    if re.match("lavo ", command): commands = command.split(" ", 1)[1].split(",",1); return Alliance.getAlliance(commands[0]).setWinInstruction(commands[1])
                    if re.match("lavl ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setWinAlliance(commands[1])
                    if re.match("lpvl ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).removeWinAlliance(commands[1])
                    if command == "p": return printAdminUserCommands()
                    if command == "pl": return User.listUsersForAdmin()
                    if re.match("pu ", command): commands = command.split(" ", 1)[1].split(","); return User.createUser(commands[0], commands[1], commands[2], commands[3], commands[4])
                    if re.match("pp ", command): return User.getUser(command.split(" ", 1)[1]).delete()
                    if re.match("pai ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setId(commands[1])
                    if re.match("pan ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setName(commands[1])
                    if re.match("pas ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setPassword(commands[1])
                    if re.match("pav ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setNation(commands[1])
                    if re.match("pal ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setAlliance(commands[1])
                    if re.match("pavl ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setFakeAlliance(commands[1])
                    if re.match("par ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setCurrency(commands[1])
                    if re.match("paht ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setKnownUser(User.getUser(commands[1]))
                    if re.match("ppht ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).removeKnownUser(User.getUser(commands[1]))
                    if re.match("palt ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setKnownPlayerAlliance(User.getUser(commands[1]))
                    if re.match("pplt ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).removeKnownPlayerAlliance(User.getUser(commands[1]))
                    if re.match("puep ", command): return User.createNPC(command.split(" ", 1)[1])
                    if re.match("pah ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setChallengeDone(Challenge.getChallenge(commands[1]))
                    if re.match("pph ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).removeChallengeDone(Challenge.getChallenge(commands[1]))
                    if command == "v": return printAdminMessageCommands()
                    if command == "vl": return Message.listMessagesForAdmin()
                    if re.match("vu kaikki,", command): message = command.split("vu kaikki,")[1]; return current_user.adminSendMessageToAll(message)
                    if re.match("vu ", command): commands = command.split(" ", 1)[1].split(",", 1); return Message.createMessage(commands[0], commands[1])
                    if re.match("vp ", command): return Message.getMessage(command.split(" ", 1)[1]).delete()
                    if re.match("vai ", command): commands = command.split(" ", 1)[1].split(","); return Message.getMessage(commands[0]).setId(commands[1])
                    if re.match("vap ", command): commands = command.split(" ", 1)[1].split(","); return Message.getMessage(commands[0]).setPlayer(commands[1])
                    if re.match("vav ", command): commands = command.split(" ", 1)[1].split(","); return Message.getMessage(commands[0]).setMessage(commands[1])
                    if re.match("vaa ", command): commands = command.split(" ", 1)[1].split(","); return Message.getMessage(commands[0]).setTimestamp(commands[1])
                    if re.match("val ", command): commands = command.split(" ", 1)[1].split(","); return Message.getMessage(commands[0]).setRead()
                    if command == "t": return printAdminTaskCommands()
                    if command == "tl": return Task.listTasksForAdmin()
                    if re.match("tu ", command): commands = command.split(" ", 1)[1].split(",", 4); return Task.createTask(commands[0], commands[1], commands[2], commands[3])
                    if re.match("tp ", command): return Task.getTask(command.split(" ")[1]).delete()
                    if re.match("tai ", command): commands = command.split(" ", 1)[1].split(","); return Task.getTask(commands[0]).setId(commands[1])
                    if re.match("tan ", command): commands = command.split(" ", 1)[1].split(","); return Task.getTask(commands[0]).setName(commands[1])
                    if re.match("tap ", command): commands = command.split(" ", 1)[1].split(","); return Task.getTask(commands[0]).setReward(commands[1])
                    if re.match("tas ", command): commands = command.split(" ", 1)[1].split(","); return Task.getTask(commands[0]).setSecret(commands[1])
                    if re.match("tak ", command): commands = command.split(" ", 1)[1].split(",", 1); return Task.getTask(commands[0]).setDescription(commands[1])
                    if re.match("tat ", command): commands = command.split(" ", 1)[1].split(","); return Task.getTask(commands[0]).setClaim(commands[1])
                    if re.match("tpt ", command): return Task.getTask(command.split(" ")[1]).unclaim()
                    if command == "s": return printAdminSecretCommands()
                    if command == "sl": return Secret.listSecretsForAdmin()
                    if re.match("su ", command): commands = command.split(" ", 1)[1].split(","); return Secret.createSecret(commands[0], commands[1])
                    if re.match("sp ", command): return Secret.getSecret(command.split(" ")[1]).delete()
                    if re.match("sai ", command): commands = command.split(" ", 1)[1].split(","); return Secret.getSecret(commands[0]).setId(commands[1])
                    if re.match("sat ", command): commands = command.split(" ", 1)[1].split(","); return Secret.getSecret(commands[0]).setTier(commands[1])
                    if re.match("sas ", command): commands = command.split(" ", 1)[1].split(","); return Secret.getSecret(commands[0]).setSecret(commands[1])
                    if command == "h": return printAdminChallengeCommands()
                    if command == "hl": return Challenge.adminListChallenges()
                    if re.match("hu ", command): commands = command.split(" ", 1)[1].split(",", 1); return Challenge.createChallenge(commands[0], commands[1])
                    if re.match("hp ", command): return Challenge.getChallenge(command.split(" ")[1]).delete()
                    if re.match("hai ", command): commands = command.split(" ", 1)[1].split(","); return Challenge.getChallenge(commands[0]).adminSetId(commands[1])
                    if re.match("hako ", command): commands = command.split(" ", 1)[1].split(","); return Challenge.getChallenge(commands[0]).adminSetCode(commands[1])
                    if re.match("haku ", command): commands = command.split(" ", 1)[1].split(",", 1); return Challenge.getChallenge(commands[0]).adminSetDescription(commands[1])
                    if command == "peli": return printAdminGameCommands()
                    if command == "peli aloitettu": return toggleGameStart()
                    if command == "peli lopetettu": return toggleGameFinished()
                    if command == "peli info": return setGameInfoText("")
                    if command == "peli status": return game.getStatus()
                    if re.match("peli info ", command): return setGameInfoText(command.split("peli info ")[1])
                    if re.match("peli aloitus ", command): return setGameStartTime(command.split("peli aloitus ")[1])
                    if re.match("peli suurin,", command): return game.setTopChallenge(command.split("peli suurin,")[1])
                    if re.match("peli haasteet,", command): return game.setFirstChallenge(command.split("peli haasteet,")[1])

        "\n" + "[peli suurin,#] - aseta suurin suoritettu haaste" + \
        "\n" + "[peli haasteet,#] - aseta haastehtävän aloittaneiden #"


        if not current_user.is_authenticated:
            return tryLogin(command)

        return "Tuntematon komento - [?] näyttää komennot"
    except Exception as e:
        print("VIRHE: " + current_user.name + ":" + path + " > " + command + " | " + str(e))
        return "Virhe - kokeile uudestaan"
