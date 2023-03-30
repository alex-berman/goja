var participant;
var role;

const socket = createSocket();

function validateWebSocketsAndStartExperiment() {
    console.log('sending start');
    socket.emit('start', (response) => {
        console.log('got response: ' + response);
        if(response) {
            const participant = response;
            location.href = '?participant=' + participant;
        }
        else {
            alert('Sorry, something went wrong when connecting to the server. You could try refreshing the page.');
        }
    });
}

function emitProceed() {
    socket.emit('proceed', { participant: participant });
}

function initializeParticipation() {
    if(participant) {
        socket.emit('request_content', { participant: participant });
    }
}

socket.on('content', (content) => {
    document.getElementById('content').innerHTML = content;
});

socket.on('redirect', (args) => {
    location.href = args.href;
});
