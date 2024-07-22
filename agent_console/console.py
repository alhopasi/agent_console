import re
from agent_console.models import User

def parseMessage(msg):
    return re.match("^[a-zA-Z0-9äÄöÖåÅ\?,. ]*$", msg)

def buildTitle():
    title = '## AGENT CONSOLE ##'
    return title

def buildUserInfo():
    userInfo = ""
    return userInfo

def buildCommands():
    commands = "[c] - clears console"
    commands = "[b] - back to main screen"
    return commands

def buildResponse(msg):
    response = msg
    return response


def tryLogin(msg):
    user = User.query.filter_by(password=msg).first()
    if user: print(user.user); return True
    else: return False

def handleMessage(command, path):
    response = ""
    if command == "": response = "[?] - help"
    if command == "c": response = "console.clear" + "\r\n" + buildTitle()
    if command == "?": response = "console.clear" + "\r\n" + buildTitle() + "\r\n" + buildUserInfo() + "\r\n" + buildCommands()
    if (command == "m" and path == "/"): response = "console.changePath messages"
    if (command == "m" and path == "/"): response = "console.changePath admin" #check if user is logged in and admin role
    if command == "b": response = "console.changePath /"

    if not parseMessage(command): response = "No cheating!"

    if response: return response

    logged_in = False
    if not logged_in:
        if not tryLogin(command): return "Login failed"
        return "Login ok!"

    return buildResponse(command)
    
