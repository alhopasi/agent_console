from flask_login import login_user, logout_user, current_user, login_required
import re
from agent_console.models import User

def parseMessage(msg):
    return re.match("^[a-zA-Z0-9äÄöÖåÅ\?,. ]*$", msg)

def buildTitle():
    title = '## AGENT CONSOLE ##'
    return title

def buildUserInfo():
    userInfo = "nation: " + current_user.nation + \
        "\n" + "currency: " + current_user.currency + \
        "\n" + "alliance: " + current_user.alliance
    return userInfo

def buildCommands(path):
    commands = "[?] - help" + \
        "\n" + "[c] - clear"
    if current_user.is_authenticated:
        if current_user.role == "user": commands += "\n" + "[u] - user info"
        if path == "/" and current_user.role == "user":
            commands += "\n" + "[m] - messages"
        if path == "/" and current_user.role == "admin":
            commands += "\n" + "[a] - admin commands"
        if path != "/":
            commands += "\n" + "[b] - back"
        commands += "\n" + "[l] - logout"
    return commands


def tryLogin(msg):
    user = User.query.filter_by(password=msg).first()
    if user: login_user(user); return True
    else: return False

def handleMessage(command, path):
    response = ""
    if not parseMessage(command): response = "No cheating!"

    if command == "": response = "[?] - help"
    if command == "c": response = "console.clear" + "\n" + buildTitle()
    if command == "?": response = buildCommands(path)
    if current_user.is_authenticated:
        if current_user.role == "user" and command == "u": response = buildUserInfo()
        if path == "/" and current_user.role == "user" and command == "m": response = "console.changePath messages"
        if path == "/" and current_user.role == "admin" and command == "a": response = "console.changePath admin"
        if path != "/" and command == "b": response = "console.changePath /"
        if command == "l": response = "console.changePath /" + "\n" + "console.clear" + "\n" + "console.changeUser " + "\n" + buildTitle(); logout_user()

    if response: return response

    if not current_user.is_authenticated:
        if not tryLogin(command): return "Login failed"
        if current_user.role == "user":
            return "Login ok! - welcome " + current_user.nation + \
            "\n" + "console.changeUser " + current_user.nation
        else: return "Login ok! - welcome " + current_user.user + \
            "\n" + "console.changeUser " + current_user.user +"@"

    return command
    
