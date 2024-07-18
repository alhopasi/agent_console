import re

def parseMessage(msg):
    return re.match("^[a-zA-Z0-9äÄöÖåÅ\? ]*$", msg)

def buildTitle():
    title = '## AGENT CONSOLE ##'
    return title

def buildUserInfo():
    userInfo = ""
    return userInfo

def buildCommands():
    commands = "[c] - clears console"
    return commands

def buildResponse(msg):
    response = msg
    return response


def tryLogin(msg):
    return False  

def handleMessage(msg):
    response = ""
    if msg == "": response = "[?] - help"
    if msg == "c": response = "console.clear" + "\r\n" + buildTitle()
    if msg == "?": response = "console.clear" + "\r\n" + buildTitle() + "\r\n" + buildUserInfo() + "\r\n" + buildCommands()

    if not parseMessage(msg): response = "No cheating!"

    if response: return response

    logged_in = False
    if not logged_in:
        if not tryLogin(msg): return "Login failed"

    return buildResponse(msg)
    
