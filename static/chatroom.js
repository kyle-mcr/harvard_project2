document.addEventListener('DOMContentLoaded', () => {

    // Open new request to get previous messages
    const request = new XMLHttpRequest();
    request.open("POST", "/listmessages");

    // Callback function for when request completes
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        localStorage.setItem("chat_id", data["chat_id"])
        let i;
        for ( i=0; i<data["message"].length; i++) {
            const li = document.createElement('li');
            const response = data["message"][i];

            // Used innerHTML instead of innerText to keep it raw
            li.innerHTML = `<strong>${response["user_name"]}</strong> : <span class="mx-4"><big>${response["selection"]}</big></span> <small>${response["time"]}</small>`;
            document.querySelector('#messages').append(li);
        }
    };
    request.send();



    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected configure button
    socket.on('connect', () => {

        // Button should emit a 'submit message' event
        document.querySelector('button').onclick = function () {
            const selection = document.querySelector('input').value;
            this.form.reset();
            socket.emit('submit message', {'selection': selection});
        };
    });

    // When a message is sent, add to the unordered list
    socket.on ('cast message', data => {
        if (data["chat_id"] === localStorage.chat_id) {
            const li = document.createElement('li');

            // Used innerHTML instead of innerText to keep it raw
            li.innerHTML = `<strong>${data["user_name"]}</strong> : <span class="mx-4"><big>${data["selection"]}</big></span> <small>${data["time"]}</small>`;
            document.querySelector('#messages').append(li);
        }
    });


});