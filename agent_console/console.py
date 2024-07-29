from flask_login import login_user, logout_user, current_user
import re
from agent_console.models import User
from agent_console.models import Alliance
from agent_console.models import Message
from agent_console.models import Task

def parseMessage(msg):
    return re.match("^[a-zA-Z0-9äÄöÖåÅ\?\!,. :\-]*$", msg)

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
                        "\n" + "[p] - pelaajat"
        commands += "\n" + "[!] - kirjaudu ulos"

        if current_user.role == "player":
            commands += "\n"
            if path == "/":
                commands += "\n" + "[v] - viestit" + \
                            "\n" + "[t] - tehtävät" + \
                            "\n" + "[a] - agenttitoiminnot"
            if path == "viestit":
                commands += "\n" + "[v] - listaa viestit" + \
                            "\n" + "[l #] - lue viesti #"
            if path == "tehtävät":
                commands += "\n" + "[t] - listaa tehtävät" + \
                            "\n" + "[salaisuus] - suorita tehtävä salaisuudella"

        if current_user.role == "admin":
            commands += "\n"
            if path == "/":
                commands += "\n" + "[a] - admin-komennot"
            if path == "admin":
                commands += "\n" + "[l] - hallitse liittoja" + \
                            "\n" + "[p] - hallitse pelaajia" + \
                            "\n" + "[v] - hallitse viestejä" + \
                            "\n" + "[t] - hallitse tehtäviä"
    return commands

def printAdminAllianceCommands():
    commands = "[ll] - liitot listaa" + \
        "\n" + "[lu liiton_nimi] - liitot uusi" + \
        "\n" + "[lp liiton_id] - liitot poista" + \
        "\n" + "[lai liiton_id,uusi_id] - liitot aseta id" + \
        "\n" + "[lan liiton_id,uusi_nimi] - liitot aseta nimi"
    return commands

def printAdminUserCommands():
    commands = "[pl] - pelaajat listaa" + \
        "\n" + "[pu nimi,salasana,valtio,liitto] - pelaajat uusi" + \
        "\n" + "[pp pelaajan_id] - pelaajat poista" + \
        "\n" + "[pai pelaajan_id,uusi_id] - pelaajat aseta id" + \
        "\n" + "[pan pelaajan_id,uusi_nimi] - pelaajat aseta nimi" + \
        "\n" + "[pas pelaajan_id,uusi_salasana] - pelaajat aseta salasana" + \
        "\n" + "[pav pelaajan_id,uusi_valtio] - pelaajat aseta valtio" + \
        "\n" + "[pal pelaajan_id,uusi_liitto] - pelaajat aseta liitto" + \
        "\n" + "[par pelaajan_id,uudet_rahat] - pelaajat aseta rahat"
    return commands

def printAdminMessageCommands():
    commands = "[vl] - viestit listaa" + \
        "\n" + "[vu pelaajan_id,viesti] - viestit uusi" + \
        "\n" + "[vp viestin_id] - viestit poista" + \
        "\n" + "[vai viestin_id,uusi_id] - viestit aseta id" + \
        "\n" + "[vap viestin_id,uusi_pelaajan_id] - viestit aseta pelaaja" + \
        "\n" + "[vav viestin_id,uusi_viesti] - viestit aseta viesti" + \
        "\n" + "[vaa viestin_id,uusi_aikaleima] - viestit aseta aikaleima" + \
        "\n" + "[val viestin_id] - viestit aseta luetuksi/ei-luetuksi"
    return commands

def printAdminTaskCommands():
    commands = "[tl] - tehtävät listaa" + \
        "\n" + "[tu tehtävän_nimi,palkinto,salaisuus,kuvaus] - tehtävät uusi" + \
        "\n" + "[tp tehtävän_id] - tehtävät poista" + \
        "\n" + "[tai tehtävän_id,uusi_id] - tehtävät aseta id" + \
        "\n" + "[tan tehtävän_id,uusi_nimi] - tehtävät aseta nimi" + \
        "\n" + "[tap tehtävän_id,uusi_palkinto] - tehtävät aseta palkinto" + \
        "\n" + "[tas tehtävän_id,uusi_salaisuus] - tehtävät aseta salaisuus" + \
        "\n" + "[tak tehtävän_id,uusi_kuvaus] - tehtävät aseta kuvaus" + \
        "\n" + "[tat tehtävän_id,tekijä] - tehtävät aseta tekijä" + \
        "\n" + "[tpt tehtävän_id] - tehtävät poista tekijä"
    return commands


def tryLogin(msg):
    user = User.query.filter_by(password=msg).first()
    if user:
        login_user(user)
        if current_user.role == "player":
            unreadMessageAmount = current_user.getUnreadMessagesAmount()
            if unreadMessageAmount == 1:
                unreadMessageAmount = "\n" + "Sinulla on 1 lukematon viesti"
            elif unreadMessageAmount > 1:
                unreadMessageAmount = "\n" + "Sinulla on " + str(unreadMessageAmount) + " lukematonta viestiä"
            else: unreadMessageAmount = ""
            return "Kirjautuminen onnistui. Tervetuloa " + current_user.nation + unreadMessageAmount + \
                "\n" + "console.changeUser " + current_user.nation + "@"
        else: return "Kirjautuminen onnistui. Tervetuloa " + current_user.name + \
                "\n" + "console.changeUser " + current_user.name +"@"
    else: return "Kirjautuminen epäonnistui"


def handleMessage(command, path):

    #try:
        if not parseMessage(command): return "No cheating!"

        if command == "": return "[?] - komennot"
        if command == ",": return "console.clear" + "\n" + printTitle()
        if command == ".": return "console.changePath /"
        if command == "?": return printCommands(path)
        if current_user.is_authenticated:
            if command == "!": logout_user(); return "console.changePath /" + "\n" + "console.clear" + "\n" + "console.logout" + "\n" + printTitle()

            if current_user.role == "player":
                if command == "p": return User.listPlayers()
                if command == "i": return current_user.getInfo()  # vai näytetäänkö komentorivillä?
                if path == "/" and command == "v": return "console.changePath viestit"
                if path == "/" and command == "t": return "console.changePath tehtävät"
                if path == "/" and command == "a": return "console.changePath agenttitoiminnot"
                if path == "viestit":
                    if command == "v": return current_user.messagesList()
                    if re.match("l ", command): return current_user.messagesRead(command.split(" ", 1)[1])
                if path == "tehtävät":
                    if command == "t": return Task.listTasks()
                    if command: return Task.claim(command, current_user.id)

            if current_user.role == "admin":
                if path == "/" and command == "a": return "console.changePath admin"
                if path == "admin":
                    if command == "l": return printAdminAllianceCommands()
                    if command == "ll": return Alliance.listAlliancesForAdmin()
                    if re.match("lu ", command): return Alliance.createAlliance(command.split(" ", 1)[1])
                    if re.match("lp ", command): return Alliance.getAlliance(command.split(" ", 1)[1]).delete()
                    if re.match("lai ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setId(commands[1])
                    if re.match("lan ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setName(commands[1])
                    if command == "p": return printAdminUserCommands()
                    if command == "pl": return User.listUsersForAdmin()
                    if re.match("pu ", command): commands = command.split(" ", 1)[1].split(","); return User.createUser(commands[0], commands[1], commands[2], commands[3])
                    if re.match("pp ", command): return User.getUser(command.split(" ", 1)[1]).delete()
                    if re.match("pai ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setId(commands[1])
                    if re.match("pan ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setName(commands[1])
                    if re.match("pas ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setPassword(commands[1])
                    if re.match("pav ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setNation(commands[1])
                    if re.match("pal ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setAlliance(commands[1])
                    if re.match("par ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setCurrency(commands[1])
                    if command == "v": return printAdminMessageCommands()
                    if command == "vl": return Message.listMessagesForAdmin()
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


            # path admin : command s - hallitse salaisuuksia  
            # listaa
            # luo
            # poista
            # aseta id
            # aseta kuvaus


            # path = "agenttitoiminnot":
            # varoitus, kun siirtyy tänne, että toiminnot maksavat rahaa!
            # siirrä rahaa toiselle valtiolle (s id määrä) | hinta 0
            # kirjoita viesti (k id viesti) | hinta 1
            # salaisuus (salaisuus) | hinta 3
            # paljasta kohteen todellinen liitto | hinta 5
            # yritä voittaa | hinta 5


        if not current_user.is_authenticated:
            return tryLogin(command)

        return "Tuntematon komento - [?] näyttää komennot"
    #except Exception as e:
    #    print(e)
    #    return "Unknown error happened"
    
