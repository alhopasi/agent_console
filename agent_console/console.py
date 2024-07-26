from flask_login import login_user, logout_user, current_user
import re
from agent_console.models import User
from agent_console.models import Alliance

def parseMessage(msg):
    return re.match("^[a-zA-Z0-9äÄöÖåÅ\?\!,. ]*$", msg)

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
        if current_user.role == "player": commands += "\n" + "[i] - pelaajan info"
        commands += "\n" + "[!] - kirjaudu ulos"

        if path == "/" and current_user.role == "player":
            commands += "\n" + \
                        "\n" + "[v] - viestit" + \
                        "\n" + "[t] - tehtävät"

        if current_user.role == "admin":
            commands += "\n"
        if path == "/" and current_user.role == "admin":
            commands += "\n" + "[a] - admin-komennot"
        if path == "admin" and current_user.role == "admin":
            commands += "\n" + "[l] - hallitse liittoja" + \
                        "\n" + "[p] - hallitse pelaajia"
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


def tryLogin(msg):
    user = User.query.filter_by(password=msg).first()
    if user: login_user(user); return True
    else: return False

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
                if command == "i": return current_user.getInfo()  # vai näytetäänkö komentorivillä?
                if path == "/" and command == "v": return "console.changePath viestit"
                if path == "/" and command == "t": return "console.changePath tehtävät"
            
            if current_user.role == "admin":
                if path == "/" and command == "a": return "console.changePath admin"
                if path == "admin":
                    if command == "l": return printAdminAllianceCommands()
                    if command == "ll": return Alliance.listAlliances()
                    if re.match("lu ", command): return Alliance.createAlliance(command.split(" ", 1)[1])
                    if re.match("lp ", command): return Alliance.getAlliance(command.split(" ", 1)[1]).delete()
                    if re.match("lai ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setId(commands[1])
                    if re.match("lan ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setName(commands[1])
                    if command == "p": return printAdminUserCommands()
                    if command == "pl": return User.listUsers()
                    if re.match("pu ", command): commands = command.split(" ", 1)[1].split(","); return User.createUser(commands[0], commands[1], commands[2], commands[3])
                    if re.match("pp ", command): return User.getUser(command.split(" ", 1)[1]).delete()
                    if re.match("pai ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setId(commands[1])
                    if re.match("pan ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setName(commands[1])
                    if re.match("pas ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setPassword(commands[1])
                    if re.match("pav ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setNation(commands[1])
                    if re.match("pal ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setAlliance(commands[1])
                    if re.match("par ", command): commands = command.split(" ", 1)[1].split(","); return User.getUser(commands[0]).setCurrency(commands[1])

            # path admin : command v - hallitse viestejä
            # listaa
            # luo
            # poista
            # aseta id
            # aseta viesti
            # aseta aikaleima
            # aseta luetuksi/pois (True/False)

            # path admin : command t - hallitse tehtäviä
            # listaa
            # luo
            # poista
            # aseta id
            # aseta nimi
            # aseta kuvaus
            # aseta palkinto
            # aseta salasana
            # aseta tekijä (done by player_id)

            # path admin : command s - hallitse salaisuuksia  
            # listaa
            # luo
            # poista
            # aseta id
            # aseta kuvaus

            # "player" : command: [valtiot] - listaa valtiot (järj.numero + aakkosjärjestys)

            # path = "viestit" : command: [v] - listaa viestit (järjestysnumero + saapumisaika)
            # path = "viestit" : command: [l viestin_numero] - lue (järjestysnumero + saapumisaika + kuvaus)

            # path = "tehtävä" : command: [salasana] - yrittää suorittaa tehtävän
            # path = "tehtävä" : command: [t] - listaa tehtävät

            # path = "toiminnot":
            # varoitus, kun siirtyy tänne, että toiminnot maksavat rahaa!
            # siirrä rahaa toiselle valtiolle (s id määrä) | hinta 0
            # kirjoita viesti (k id viesti) | hinta 1
            # salaisuus (salaisuus) | hinta 3
            # paljasta kohteen todellinen liitto | hinta 5
            # yritä voittaa | hinta 5


        if not current_user.is_authenticated:
            if not tryLogin(command): return "Kirjautuminen epäonnistui"
            print(current_user.role)
            if current_user.role == "player":
                return "Kirjautuminen onnistui. Tervetuloa " + current_user.nation + \
                "\n" + "console.changeUser " + current_user.nation + "@"
            else: return "Kirjautuminen onnistui. Tervetuloa " + current_user.name + \
                "\n" + "console.changeUser " + current_user.name +"@"

        return "Tuntematon komento - [?] näyttää komennot"
    #except Exception as e:
    #    print(e)
    #    return "Unknown error happened"
    
