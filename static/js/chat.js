usersOnline = document.getElementById('users');
usernameBox = document.getElementById('username');
typingParagraph = document.getElementById('typing');
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

messageBox.addEventListener('keydown', showTyping);
messageBox.addEventListener('keyup', stoppedTyping);

// Runs on the 'keydown' event on the message box.
function showTyping() {
    socket.emit('typing', usernameBox.value);
}

socket.on('show typing', (username) => {
    typingParagraph.innerHTML = `${username} is typing...`;
})

// A function that creates a synchronous sleep.
function sleep(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

// Runs on the 'keyup' event on the message box.
async function stoppedTyping() {
    await sleep(5000);
    socket.emit('nottyping');
}

socket.on('show stopped typing', function () {
    typingParagraph.innerHTML = '';

})

// Runs when the send button is clicked.
function sendData() { 
    socket.emit('nottyping');
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