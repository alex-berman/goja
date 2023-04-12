import random
from collections import defaultdict
import time

from flask_socketio import emit

from statemanagement import global_state


logger = None


def send_history(participant):
    for utterance_info in global_state.participants[participant]['dialog_history']:
        emit('utterance', utterance_info)


def handle_utterance(participant, utterance, bot, socketio):
    utterance_info = {
        'role': 'user',
        'content': utterance
    }
    participant_info = global_state.participants[participant]
    logger.info('utterance', utterance=utterance_info, participant=participant)
    participant_info['dialog_history'].append(utterance_info)
    session_id = participant_info['session_id']
    emit('utterance', utterance_info, to=session_id)
    socketio.start_background_task(
        get_and_process_response_from_bot, participant, bot, participant_info['dialog_history'], session_id, socketio)


def get_and_process_response_from_bot(participant, bot, dialog_history, session_id, socketio):
    logger.debug('getting response from bot')
    socketio.emit('bot_response_requested', to=session_id)
    utterance = ''
    deltas = bot.get_response(dialog_history)
    #socketio.sleep(3); utterance = "hej"
    for delta in deltas:
        socketio.emit('bot_utterance_delta', {'role': 'assistant', 'content': delta})
        utterance += delta
    utterance_info = {
        'role': 'assistant',
        'content': utterance
    }
    socketio.emit('bot_response_complete', to=session_id)
    logger.info('utterance', utterance=utterance_info, participant=participant)
    dialog_history.append(utterance_info)
