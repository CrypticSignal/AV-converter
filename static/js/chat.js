usersOnline = document.getElementById('users');
usernameBox = document.getElementById('username');
messageBox = document.getElementById('message');
messages = document.getElementById('messages');
sendButton = document.getElementById('sendbutton');
sendButton.addEventListener('click', sendData);

// Hitting the enter key is the same thing as clicking on the send button.
document.addEventListener("keydown", function(event) {
    if (event.keyCode === 13) {
        sendButton.click();
    }
});
    
const socket = io.connect('https://' + document.domain + ':' + location.port);

socket.on('users online', function(count) {
    usersOnline.innerHTML = `Users Online: ${count}`;
});

function sendData() { // Runs when the send button is clicked.
    const username = usernameBox.value;
    const userInput = messageBox.value;
    socket.send({
        user_name: username,
        message: userInput
    })
};

socket.on('message', function(msg) {
    if (typeof msg.user_name !== 'undefined') {
        messages.innerHTML += `<p><b>${msg.user_name}</b> said: <i>${msg.message}</i></p>`;
        messageBox.value = ''
    }   
});