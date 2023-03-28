const ROLE_LABEL = {
    'operator': 'Operator',
    'respondent': 'Test taker'
};

const socket = createSocket();
socket.on('connect', function() {
    console.log('connected to server');
    socket.emit('update_session', { participant: participant });
});

var roleOfPreviousUtterance;
var chatHistoryDiv;
var isTyping = false;
var stoppedTypingTimeoutID;
var otherRole;
var otherIsTypingDiv;

socket.on('utterance', (utterance_info) => {
    console.log('utterance:');
    console.log(utterance_info);
    removeOtherIsTypingDiv();
    chatHistoryDiv.appendChild(createUtteranceDiv(utterance_info));
    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
    roleOfPreviousUtterance = utterance_info.role;
});

socket.on('other_typing', (args) => {
    console.log('other_typing');
    console.log(args);
    handleOtherTyping(args.event);
});

function createUtteranceDiv(utterance_info) {
    var container = document.createElement('div');
    container.className = (utterance_info.role == role ? 'utterance_container_self' : 'utterance_container_other');
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
    utteranceDiv.innerHTML = utterance_info.utterance;
    utteranceBubble.appendChild(utteranceDiv);
    container.appendChild(utteranceBubble);
    return container;
}

function initializeChat() {
    document.getElementById('chat_input').focus();
    chatHistoryDiv = document.getElementById('chat_history');
    otherRole = (role == 'operator' ? 'respondent' : 'operator');
    socket.emit('request_chat_history', { participant: participant });
}

function handleKeyPress(e) {
    var code = (e.keyCode ? e.keyCode : e.which);
    if (code == 13) { //Enter keycode
        document.getElementById('chat_input').disabled = true;
        const utterance = document.getElementById('chat_input').value;
        console.log('emit utter: ' + utterance);
        socket.volatile.timeout(3000).emit('utter', {
            role: role,
            participant: participant,
            utterance: utterance
        }, (err, response) => {
            if(err) {
                console.log('timed out');
                alert('Sorry, sending the message took too long. You may try again.');
            }
            else {
                console.log('got response: ' + response);
                if(response) {
                    window.setTimeout(clearChatInput, 1);
                    if (isTyping) {
                        isTyping = false;
                        window.clearTimeout(stoppedTypingTimeoutID);
                    }
                }
                else {
                    alert('Sorry, something went wrong when sending the message.');
                }
            }
            document.getElementById('chat_input').disabled = false;
            document.getElementById('chat_input').focus();
        });
    }
    else {
        if (isTyping) {
            window.clearTimeout(stoppedTypingTimeoutID);
        }
        else {
            socket.volatile.emit('typing', {
                participant: participant,
                event: 'started'
            });
            isTyping = true;
        }
        stoppedTypingTimeoutID = window.setTimeout(stoppedTyping, 1000);
    }
}

function stoppedTyping() {
    socket.volatile.emit('typing', {
        participant: participant,
        event: 'stopped'
    });
    isTyping = false;
}

function clearChatInput() {
    document.getElementById('chat_input').value = '';
}

function handleOtherTyping(event) {
    if (event == 'started') {
        handleOtherStartedTyping();
    } else if (event == 'stopped') {
        handleOtherStoppedTyping();
    }
}

function handleOtherStartedTyping() {
    if (otherIsTypingDiv) {
        otherIsTypingDiv.style.visibility = 'visible';
    }
    else {
        removeOtherIsTypingDiv();
        otherIsTypingDiv = createOtherIsTypingDiv();
        chatHistoryDiv.appendChild(otherIsTypingDiv);
        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
    }
}

function removeOtherIsTypingDiv() {
    if (otherIsTypingDiv) {
        chatHistoryDiv.removeChild(otherIsTypingDiv);
        otherIsTypingDiv = null;
    }
}

function createOtherIsTypingDiv() {
    var container = document.createElement('div');
    container.className = 'utterance_container_other';
    var roleDiv = document.createElement('div');
    roleDiv.className = 'role';
    roleDiv.innerHTML = ROLE_LABEL[otherRole] + ' is typing...';
    container.appendChild(roleDiv);
    return container;
}

function handleOtherStoppedTyping() {
    if (otherIsTypingDiv) {
        otherIsTypingDiv.style.visibility = 'hidden';
    }
}