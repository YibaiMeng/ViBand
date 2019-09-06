"use strict";
let reveal_handler = null;
let ws = new WebSocket("wss://viband.mengyibai.cn/viband");
ws.onopen = function (event) {
    true;
    //let ele = document.getElementById("connection_status")
    //ele.innerHTML = "Websocket opened!"
    //ws.send(JSON.stringify({action: 'start_state', value : Reveal.getState()}));
};
ws.onmessage = function (event) {
    //let ele = document.getElementById("message")
    let user_ele = document.getElementById("user")
    let data = JSON.parse(event.data);
    switch (data.type) {
        case 'state':
            //ele.textContent = data.value["indexh"];
            if (reveal_handler) {
                reveal_handler.setState(data.value);
            }
            break;
        case 'users':
            user_ele.textContent = (
                data.count.toString() + " user" +
                (data.count == 1 ? "" : "s"));
            break;
        default:
            console.error(
                "unsupported event", data);
    }
}

