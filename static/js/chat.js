usersOnline = document.getElementById('users');
usernameBox = document.getElementById('username');
messageBox = document.getElementById('message');
messages = document.getElementById('messages');
sendButton = document.getElementById('sendbutton');
sendButton.addEventListener('click', sendData);

// Hitting the enter key is the same thing as clicking on the send button.
document.addEventListener("keydown", (event) => {
    if (event.keyCode === 13) {
        sendButton.click();
    }
});
    
const socket = io.connect('https://' + document.domain + ':' + location.port);

socket.on('user connected', (count) => {
    if (count > 1) {
        usersOnline.innerHTML = `Users Online: ${count}`;
        messages.innerHTML += '<p>A user has connected!</p>';
    }
    else {
        usersOnline.innerHTML = `Users Online: ${count}`;
    }
});

socket.on('user disconnected', (count) => {
    usersOnline.innerHTML = `Users Online: ${count}`;
    messages.innerHTML += '<p>A user disconnected.</p>';
});

function sendData() { // Runs when the send button is clicked.
    const username = usernameBox.value;
    const userInput = messageBox.value;
    socket.emit('message sent', {
        user_name: username,
        message: userInput
    })
};

socket.on('show message', (message) => {
    if (typeof message.user_name !== 'undefined') {
        messages.innerHTML += `<p><b>${message.user_name}</b>: <i>${message.message}</i></p>`;
        messageBox.value = ''
        messageBox.focus();
    }   
});