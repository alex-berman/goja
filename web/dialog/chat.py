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
    global_state.participants[participant]['dialog_history'].append(utterance_info)
    return True
