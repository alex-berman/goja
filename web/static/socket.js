function getUrlPrefix() {
    const firstSlashIndex = location.pathname.indexOf('/');
    const secondSlashIndex = location.pathname.indexOf('/', firstSlashIndex + 1);
    if(secondSlashIndex == -1) {
        return '';
    }
    else {
        return location.pathname.slice(0, secondSlashIndex);
    }
}

function createSocket() {
    const socket = io(
        location.protocol + '//' + location.host, {
            path: getUrlPrefix() + '/socket.io/',
            transports: ['polling']
        });
    socket.on('connect', function() {
        console.log('connected to server');
    });
    socket.io.on("error", (error) => {
        console.log('Socket error: ' + error);
    });
    return socket;
}

