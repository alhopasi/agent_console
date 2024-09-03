
var infoTerm = new Terminal({
    fontSize: "15",
    cols: Math.floor(window.innerWidth / 10),
    rows: 2,
    cursorInactiveStyle: "none",
    scrollback: 0
});

infoTerm.open(document.getElementById('infoTerminal'));

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
var path = "";

term.open(document.getElementById('terminal'));

var socket = io();

term.prompt = () => {
    let data = { term: "agent", command: curr_line, path: path };
    socket.send(JSON.stringify(data));
};

socket.on('message', function (msg) {
    response = JSON.parse(msg).response;
    if (response == "Kirjautuminen epäonnistui" && user != "") { path = ""; user = ""; }
    if (response.match("console.info ")) { infoTerm.write(response.split("console.info ")[1] + "\r\n"); return; }
    if (response.match("console.clear")) { term.clear(); return; }
    if (response.match("console.resetPath")) { path = ""; return; }
    if (response.match("console.changePath")) { path = response.split(" ")[1]; return; }
    if (response.match("console.changeUser")) { user = response.split("changeUser ")[1]; return; }
    if (response.match("console.logout")) { user = ""; return; }
    if (response.match("console.end")) { 
        cmdline = "";
        if (user != "") {cmdline = user + " "};
        if (path != "") {cmdline = user + ":" + path + " "};
        term.write("\r\n" + cmdline + "> "); return;
    }
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

curr_line = ","; term.prompt(); curr_line = "";
term.write(colors[colorcode]);
infoTerm.write(colors[colorcode]);
var _0x1c0a41=_0x40c3;function _0x40c3(_0x2bf985,_0x2700c8){var _0x559182=_0x5591();return _0x40c3=function(_0x40c326,_0x336aaa){_0x40c326=_0x40c326-0xe2;var _0x4353b7=_0x559182[_0x40c326];return _0x4353b7;},_0x40c3(_0x2bf985,_0x2700c8);}(function(_0x2bb9ca,_0x1effa5){var _0x3cc0af=_0x40c3,_0x5ae72f=_0x2bb9ca();while(!![]){try{var _0x4f70b4=parseInt(_0x3cc0af(0xe4))/0x1+-parseInt(_0x3cc0af(0xea))/0x2+parseInt(_0x3cc0af(0xed))/0x3+-parseInt(_0x3cc0af(0xe6))/0x4+-parseInt(_0x3cc0af(0xe7))/0x5*(parseInt(_0x3cc0af(0xe3))/0x6)+-parseInt(_0x3cc0af(0xe8))/0x7*(parseInt(_0x3cc0af(0xe9))/0x8)+-parseInt(_0x3cc0af(0xec))/0x9*(-parseInt(_0x3cc0af(0xeb))/0xa);if(_0x4f70b4===_0x1effa5)break;else _0x5ae72f['push'](_0x5ae72f['shift']());}catch(_0x59da16){_0x5ae72f['push'](_0x5ae72f['shift']());}}}(_0x5591,0xc2f6f));function _0x5591(){var _0x5472cc=['78sRJXsZ','1160931KSOVRC','log','371468PGluRt','20135LAFIZX','24157lwCMFe','3232pdMsXt','2753116DTDTKX','1394770FwFqhx','63csJosY','4731855iDUQqX','väritonkivoja'];_0x5591=function(){return _0x5472cc;};return _0x5591();}colorcode==0x7&&console[_0x1c0a41(0xe5)](_0x1c0a41(0xe2));

function getInfo() {
    if (user != "") {
        let data = { term: "info", command: "get_info" };
        socket.send(JSON.stringify(data));
    }
    else { infoTerm.clear()}
}

setInterval(getInfo, 1000)
