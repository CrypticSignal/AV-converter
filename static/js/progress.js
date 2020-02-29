$(document).ready(function(){ 
    //connect to the socket server.
    var socket = io.connect('https://' + document.domain + ':' + location.port);
    var test_received = [];

    // this is a callback that triggers when the "show progress" event is emitted by the server.
    socket.on('show progress', function(msg) {
        // Just show one line
        if (test_received.length >= 1){
            test_received.shift()
        }            
        test_received.push(msg.number);
        progress = '';
        for (var i = 0; i < test_received.length; i++){
            progress = progress + '<p>' + test_received[i].toString() + '</p>';
        }
        $('#log').html(progress);
    });

});