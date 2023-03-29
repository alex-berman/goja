import random
from collections import defaultdict
import time

from flask_socketio import emit

from statemanagement import global_state


logger = None


def send_history(participant):
    for utterance_info in global_state.participants[participant]['dialog_history']:
        emit('utterance', utterance_info)


def handle_utterance(participant, utterance, bot):
    utterance_info = {
        'role': 'user',
        'content': utterance
    }
    participant_info = global_state.participants[participant]
    participant_info['dialog_history'].append(utterance_info)
    session_id = participant_info['session_id']
    emit('utterance', utterance_info, to=session_id)
    get_and_process_response_from_bot(bot, participant_info['dialog_history'], session_id)
    return True


def get_and_process_response_from_bot(bot, dialog_history, session_id):
    utterance = bot.get_response(dialog_history)
    utterance_info = {
        'role': 'assistant',
        'content': utterance
    }
    dialog_history.append(utterance_info)
    emit('utterance', utterance_info, to=session_id)
