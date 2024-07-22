
var term = new Terminal({
    cursorBlink: "block"
});

var curr_line = "";
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
    if (response.match("console.end")) { term.write("\r\n" + path + "$ "); return; }
    term.write(response + "\r\n");
    
});

term.onKey(function (data) {
    kc = data.domEvent.key
    if (kc == "Enter") {
        term.prompt();
        term.write("\r\n");
        curr_line = "";
    } else if (kc == "Backspace") {
        if (curr_line) {
            curr_line = curr_line.slice(0, curr_line.length - 1);
            term.write("\b \b");
        }
    } else if (kc.match("^[a-zA-Z0-9äÄöÖåÅ\?,. ]$")) {
        curr_line += data.key;
        term.write(data.key);
    }
});

curr_line = "c"; term.prompt(); curr_line = "";
