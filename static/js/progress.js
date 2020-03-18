
$(document).ready(function(){ 
    //connect to the socket server.
    const socket = io.connect('https://' + document.domain + ':' + location.port);
    var text_received = [];
    console.log(document.domain)
    console.log(location.port)
    // this is a callback that triggers when the "show progress" event is emitted by the server.
    socket.on('show progress', function(msg) {
        // Just show one line
        if (text_received.length >= 1){
            text_received.shift()
        }            
        text_received.push(msg.progress);
        var progress = '';
        for (var i = 0; i < text_received.length; i++){
            progress = '<p>' + text_received[i].toString() + '</p>';
        }
        $('#log').html(progress);
        console.log("This is progress: " + progress)
    });

});