
var term = new Terminal({
    cursorBlink: "block",
    fontSize: "15",
    cols: Math.floor(window.innerWidth / 10),
    rows: Math.floor(window.innerHeight / 20)
});

addEventListener("resize", (event) => {});
onresize = (event) => {
    cols = Math.floor(window.innerWidth / 10);
    rows = Math.floor(window.innerHeight / 20);
    term.resize(cols, rows)
};

var curr_line = "";
var user = "";
var path = "/";

term.open(document.getElementById('terminal'));

var socket = io();

term.prompt = () => {
    let data = { command: curr_line, path: path };
    socket.send(JSON.stringify(data));
};

socket.on('message', function (msg) {
    response = JSON.parse(msg).response;

    if (response.match("console.clear")) { term.clear(); return; }
    if (response.match("console.changePath")) { path = response.split(" ")[1]; return; }
    if (response.match("console.changeUser")) { user = response.split("changeUser ")[1]; return; }
    if (response.match("console.logout")) { user = ""; return; }
    if (response.match("console.end")) { term.write("\r\n" + user + path + "$ "); return; }
    term.write(response + "\r\n");
    
});

term.onKey(function (data) {
    kc = data.domEvent.key;
    if (kc == "Enter") {
        term.prompt();
        term.write("\r\n");
        curr_line = "";
    } else if (kc == "Backspace") {
        if (curr_line) {
            curr_line = curr_line.slice(0, curr_line.length - 1);
            term.write("\b \b");
        }
    }
});

term.onData(function (data) {
    if (data.match("^[a-zA-Z0-9äÄöÖåÅ\?\!,. :\-]$")) {
        curr_line += data;
        term.write(data);
    }
});

const RED = "\u001b[31m";
const GREEN = "\u001b[32m";
const YELLOW = "\u001b[33m";
const BLUE = "\u001b[34m";
const MAGENTA = "\u001b[35m";
const CYAN = "\u001b[36m";
const WHITE = "\u001b[37m";
const PINK = "\u001b[38;5;201m";
const LAVENDER = "\u001b[38;5;147m";
const AQUA = "\u001b[38;2;145;231;255m";
const PENCIL = "\u001b[38;2;253;182;0m";

colors = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, PINK, LAVENDER, AQUA, PENCIL]
colorcode = Math.floor(Math.random() * 11)

curr_line = ","; term.prompt(); curr_line = ""; term.write(colors[colorcode])
