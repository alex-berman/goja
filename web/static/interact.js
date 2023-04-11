const ROLE_LABEL = {
    'user': 'You',
    'assistant': 'Bot'
};

const socket = createSocket();
socket.on('connect', function() {
    console.log('connected to server');
    socket.emit('update_session', { participant: participant });
});

socket.on('redirect', (args) => {
    location.href = args.href;
});

var roleOfPreviousUtterance;
var chatHistoryDiv;
var caseAssessmentDiv;
var numCases;

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
    utteranceDiv.innerHTML = formatUtterance(utterance_info.content);
    utteranceBubble.appendChild(utteranceDiv);
    container.appendChild(utteranceBubble);
    return container;
}

function formatUtterance(utterance) {
  var replacement = utterance.replace('\n', '<br>');
  if(replacement.includes('\n')) {
    return formatUtterance(replacement);
  }
  else {
    return replacement;
  }
}

function initializeInteraction() {
  caseAssessmentDiv = document.getElementById('case_assessment_div');
  socket.emit('get_state', { participant: participant });
}

socket.on('state', (state) => {
    console.log('state:');
    console.log(state);
    if(state == 'assess_without_bot') {
      socket.emit('get_case', { participant: participant });
    }
    else if(state == 'assess_with_bot') {
      document.getElementById('chat_input').focus();
      chatHistoryDiv = document.getElementById('chat_history');
      socket.emit('get_case', { participant: participant });
      socket.emit('request_chat_history', { participant: participant });
    }
});

socket.on('case', (payload) => {
    console.log('case:');
    console.log(payload);
    var caseInfoDiv = document.getElementById('case_info_div');
    currentCase = payload;
    caseInfoDiv.innerHTML = caseInfoAsHTML(currentCase.features);
    caseAssessmentDiv.style.visibility = 'visible';
    updateAssessmentOptions(currentCase.assessment);
    updateNavigation();
});

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

function selectCaseAssessmentOption(label) {
  socket.emit('update_assessment', {
      participant: participant,
      case_index: currentCase.index,
      state: currentCase.state,
      assessment: label
  });
}

function updateAssessmentOptions(selectedLabel) {
    for (var label in assessmentLabels) {
      var div = document.getElementById('case_assessment_option_' + label);
      div.className = (label == selectedLabel) ? 'case_assessment_option case_assessment_option_selected' : 'case_assessment_option';
    };
}

function updateNavigation() {
  var div = document.getElementById('caseCountIndicator');
  div.innerHTML = 'Case ' + currentCase.count + ' / ' + numCases;
  var buttonPrevious = document.getElementById('buttonPrevious');
  buttonPrevious.disabled = (currentCase.count <= 1);
  var buttonNext = document.getElementById('buttonNext');
  buttonNext.disabled = !currentCase || currentCase.assessment === null;
}

function proceedWithinCases(step) {
  socket.emit('proceed_within_cases', {
      participant: participant,
      step: step
  });
}
