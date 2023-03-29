import random
from collections import defaultdict
import time

from flask_socketio import emit

from statemanagement import global_state


logger = None


def send_history(participant):
    for utterance_info in global_state.participants[participant]['dialog_history']:
        emit('utterance', utterance_info)


def handle_utterance(participant, utterance):
    utterance_info = {
        'role': 'user',
        'utterance': utterance
    }
    participant_info = global_state.participants[participant]
    participant_info['dialog_history'].append(utterance_info)
    session_id = participant_info['session_id']
    emit('utterance', utterance_info, to=session_id)
    return True
