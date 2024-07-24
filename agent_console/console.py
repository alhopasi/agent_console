from flask_login import login_user, logout_user, current_user
import re
from agent_console.models import User
from agent_console.models import Alliance

def parseMessage(msg):
    return re.match("^[a-zA-Z0-9äÄöÖåÅ\?,. ]*$", msg)

def printTitle():
    title = '## AGENT CONSOLE ##'
    return title

def buildUserInfo():
    userInfo = "nation: " + current_user.nation + \
        "\n" + "currency: " + current_user.currency + \
        "\n" + "alliance: " + current_user.alliance
    return userInfo

def printCommands(path):
    commands = "[?] - help" + \
        "\n" + "[c] - clear"
    if current_user.is_authenticated:
        if current_user.role == "user": commands += "\n" + "[u] - user info"
        if path == "/" and current_user.role == "user":
            commands += "\n" + "[m] - messages"
        if path != "/":
            commands += "\n" + "[b] - back"
        commands += "\n" + "[l] - logout"

        if current_user.role == "admin":
            commands += "\n\n" + "admin commands:"
        if path == "/" and current_user.role == "admin":
            commands += "\n" + "[a] - admin panel"
        if path == "admin" and current_user.role == "admin":
            commands += "\n" + "[la] - list alliances" + \
                        "\n" + "[ca alliance_name] - create new alliance" + \
                        "\n" + "[da alliance_id] - delete alliance" + \
                        "\n" + "[sai alliance_id,new_alliance_id] - set alliance id" + \
                        "\n" + "[san alliance_id,new_alliance_name] - set alliance name" + \
                        "\n" + "[lu] - list users" + \
                        "\n" + "[cu user_name,password,nation,alliance] - create new user" + \
                        "\n" + "[du id] - delete user"
                        

    return commands


def tryLogin(msg):
    user = User.query.filter_by(password=msg).first()
    if user: login_user(user); return True
    else: return False

def handleMessage(command, path):

    #try:
        if not parseMessage(command): return "No cheating!"

        if command == "": return "[?] - help"
        if command == "c": return "console.clear" + "\n" + printTitle()
        if command == "?": return printCommands(path)
        if current_user.is_authenticated:
            if current_user.role == "user" and command == "u": return buildUserInfo()
            if path == "/" and current_user.role == "user" and command == "m": return "console.changePath messages"

            if path != "/" and command == "b": return"console.changePath /"
            if command == "l": logout_user(); return "console.changePath /" + "\n" + "console.clear" + "\n" + "console.logout" + "\n" + printTitle()

            if path == "/" and current_user.role == "admin" and command == "a": return "console.changePath admin"
            if path == "admin" and current_user.role == "admin" and command == "la": return Alliance.listAlliances()
            if path == "admin" and current_user.role == "admin" and re.match("ca ", command): return Alliance.createAlliance(command.split(" ", 1)[1])
            if path == "admin" and current_user.role == "admin" and re.match("da ", command): return Alliance.getAlliance(command.split(" ", 1)[1]).delete()
            if path == "admin" and current_user.role == "admin" and re.match("sai ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setId(commands[1])
            if path == "admin" and current_user.role == "admin" and re.match("san ", command): commands = command.split(" ", 1)[1].split(","); return Alliance.getAlliance(commands[0]).setName(commands[1])
            if path == "admin" and current_user.role == "admin" and command == "lu": return User.listUsers()
            if path == "admin" and current_user.role == "admin" and re.match("cu ", command): commands = command.split(" ", 1)[1].split(","); return User.createUser(commands[0], commands[1], commands[2], commands[3])
            if path == "admin" and current_user.role == "admin" and re.match("du ", command): return User.getUser(command.split(" ", 1)[1]).delete()
            # lu - list users
            # cu user password nation alliance role - create new user - cu matti,elking,Example Elks,1
            # du id - delete user
            # sui id 
            # suu id user - set user user
            # sup id pw - set user password
            # sun id nation - set user nation
            # sua id id - set user alliance
            # suc id currency - set user currency

        if not current_user.is_authenticated:
            if not tryLogin(command): return "Login failed"
            if current_user.role == "user":
                return "Login ok! - welcome " + current_user.nation + \
                "\n" + "console.changeUser " + current_user.nation
            else: return "Login ok! - welcome " + current_user.name + \
                "\n" + "console.changeUser " + current_user.name +"@"

        return "Unknown command - [?] for help"
    #except Exception as e:
    #    print(e)
    #    return "Unknown error happened"
    
