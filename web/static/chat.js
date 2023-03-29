const ROLE_LABEL = {
    'user': 'You',
    'assistant': 'Bot'
};

const socket = createSocket();
socket.on('connect', function() {
    console.log('connected to server');
    socket.emit('update_session', { participant: participant });
});

var roleOfPreviousUtterance;
var chatHistoryDiv;

socket.on('utterance', (utterance_info) => {
    console.log('utterance:');
    console.log(utterance_info);
    chatHistoryDiv.appendChild(createUtteranceDiv(utterance_info));
    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
    roleOfPreviousUtterance = utterance_info.role;
});

function createUtteranceDiv(utterance_info) {
    var container = document.createElement('div');
    container.className = 'utterance_container_' + utterance_info.role;
    if(utterance_info.role != roleOfPreviousUtterance) {
        var roleDiv = document.createElement('div');
        roleDiv.className = 'role';
        roleDiv.innerHTML = (utterance_info.role == role ? 'You' : ROLE_LABEL[utterance_info.role]);
        container.appendChild(roleDiv);
    }
    var utteranceBubble = document.createElement('div');
    utteranceBubble.classList.add('utterance_bubble');
    utteranceBubble.classList.add('background_' + utterance_info.role);
    var utteranceDiv = document.createElement('div');
    utteranceDiv.className = 'utterance';
    utteranceDiv.innerHTML = utterance_info.content.replaceAll('\n', '<br>');
    utteranceBubble.appendChild(utteranceDiv);
    container.appendChild(utteranceBubble);
    return container;
}

function initializeChat() {
    document.getElementById('chat_input').focus();
    chatHistoryDiv = document.getElementById('chat_history');
    socket.emit('request_chat_history', { participant: participant });
}

function handleKeyPress(e) {
    var code = (e.keyCode ? e.keyCode : e.which);
    if (code == 13) { //Enter keycode
        const utterance = document.getElementById('chat_input').value;
        console.log('emit utter: ' + utterance);
        socket.emit('utter', {
            participant: participant,
            utterance: utterance
        });
        window.setTimeout(clearChatInput, 1);
    }
}

function clearChatInput() {
    document.getElementById('chat_input').value = '';
}
