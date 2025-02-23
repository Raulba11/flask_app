document.addEventListener('DOMContentLoaded', () => {
    
    // Connect to websocket
    var socket = io.connect();

    // Retrieve username
    const username = document.querySelector('#get-username').innerHTML;

    // Set default room
    let room = "Lounge"
    joinRoom("Lounge");

    // Send messages
    document.querySelector('#send_message').onclick = () => {
        socket.emit('incoming-msg', {
            'msg': document.querySelector('#user_message').value,
            'username': username, 'room': room
        });

        document.querySelector('#user_message').value = '';
    };

    // Display all incoming messages
    socket.on('message', data => {

        // Display current message
        if (data.msg) {
            const span_username = document.createElement('span');
            const span_timestamp = document.createElement('span');
            const br = document.createElement('br');
            const div = document.createElement('div');
            // Display user's own message
            if (data.username == username) {
                div.setAttribute("class", "my-msg");

                // Username
                span_username.setAttribute("class", "my-username");
                span_username.innerText = data.username;

                // Timestamp
                span_timestamp.setAttribute("class", "timestamp");
                span_timestamp.innerText = data.time_stamp;

                // HTML to append
                div.innerHTML += span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML

                //Append
                document.querySelector('#display-message-section').append(div);
            }
            // Display other users' messages
            else if (typeof data.username !== 'undefined') {
                div.setAttribute("class", "others-msg");

                // Username
                span_username.setAttribute("class", "other-username");
                span_username.innerText = data.username;

                // Timestamp
                span_timestamp.setAttribute("class", "timestamp");
                span_timestamp.innerText = data.time_stamp;

                // HTML to append
                div.innerHTML = span_username.outerHTML + br.outerHTML + data.msg + br.outerHTML + span_timestamp.outerHTML

                //Append
                document.querySelector('#display-message-section').append(div);
            }
            // Display system message
            else {
                printSysMsg(data.msg);
            }


        }
        scrollDownChatWindow();
    });

    // Select a room
    document.querySelectorAll('.select-room').forEach(p => {
        p.onclick = () => {
            let newRoom = p.innerHTML
            // Check if user already in the room
            if (newRoom === room) {
                msg = `You are already in ${room} room.`;
                printSysMsg(msg);
            } else {
                leaveRoom(room);
                joinRoom(newRoom);
                room = newRoom;
            }
        };
    });

    // Logout from chat
    document.querySelector("#logout-btn").onclick = () => {
        leaveRoom(room);
    };

    // Trigger 'leave' event if user was previously on a room
    function leaveRoom(room) {
        socket.emit('leave', { 'username': username, 'room': room });

        document.querySelectorAll('.select-room').forEach(p => {
            p.style.color = "white";
        });
    }

    // Trigger 'join' event
    function joinRoom(room) {
        
        // Join room
        socket.emit('join', { 'username': username, 'room': room });
        
        // Highlight selected room
        document.querySelector('#' + CSS.escape(room)).style.color = "#ffc107";
        
        // Clear message area
        document.querySelector('#display-message-section').innerHTML = '';
        
        // Autofocus on text box
        document.querySelector("#user_message").focus();
        
        //Cargar mensajes
        socket.emit('loadHistorial', {'room': room})
    }

    // Scroll chat window down
    function scrollDownChatWindow() {
        const chatWindow = document.querySelector("#display-message-section");
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Print system messages
    function printSysMsg(msg) {
        const p = document.createElement('p');
        p.setAttribute("class", "system-msg");
        p.innerHTML = msg;
        document.querySelector('#display-message-section').append(p);
        scrollDownChatWindow()

        // Autofocus on text box
        document.querySelector("#user_message").focus();
    }
});
$(function () {

         //Al clicar al botón de gestionar salas abrir un modal con las opciones
     $('#btnConfigurarSalas').click(function(){
        $('#configSalasModal').modal('show')
    })
})