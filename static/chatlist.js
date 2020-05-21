document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected configure button
    socket.on('connect', () => {

        // Button should emit a 'submit channel' event
        document.querySelector('form button').onclick = () => {
            const selection = document.querySelector('form input').value;
            socket.emit('submit channel', {'selection': selection})
        };
    });

    // When a message is sent, add to the unordered list
    socket.on ('cast channel', data => {
        const li = document.createElement('li');

        // Used innerHTML instead of innerText to keep it raw
        li.innerHTML = `<a href="/channels/${data["chat_id"]}"> ${data["selection"]} </a>`;
        console.log(li.innerHTML);
        document.querySelector('#channels').append(li);
    });
});