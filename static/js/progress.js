$(document).ready(function(){ 
    //connect to the socket server.
    const socket = io.connect('https://' + document.domain + ':' + location.port);
    // this is a callback that triggers when the "show progress" event is emitted by the server.
    socket.on('show progress', function(msg) {      
        $('#log').html(msg.progress);  
    });
});