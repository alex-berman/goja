from flask_socketio import emit

from statemanagement import global_state


logger = None


def send_history(participant):
    dialog_histories = global_state.participants[participant]['dialog_histories']
    if len(dialog_histories) > 0:
        current_dialog_history = dialog_histories[-1]
        for utterance_info in current_dialog_history:
            emit('utterance', utterance_info)
    else:
        logger.warning("no dialog histories")


def handle_utterance(participant, utterance, bot, socketio):
    utterance_info = {
        'role': 'user',
        'content': utterance
    }
    participant_info = global_state.participants[participant]
    logger.info('utterance', utterance=utterance_info, participant=participant)
    dialog_histories = participant_info['dialog_histories']
    if len(dialog_histories) > 0:
        current_dialog_history = dialog_histories[-1]
        current_dialog_history.append(utterance_info)
        session_id = participant_info['session_id']
        emit('utterance', utterance_info, to=session_id)
        socketio.start_background_task(
            get_and_process_response_from_bot, participant, bot, current_dialog_history, session_id, socketio)
    else:
        logger.warning("no dialog histories")


def get_and_process_response_from_bot(participant, bot, dialog_history, session_id, socketio):
    logger.debug('getting response from bot')
    socketio.emit('bot_response_requested', to=session_id)
    utterance = ''
    deltas = bot.get_response(dialog_history)
    #socketio.sleep(3); utterance = "hej"
    for delta in deltas:
        socketio.emit('bot_utterance_delta', {'role': 'assistant', 'content': delta})
        utterance += delta
    socketio.emit('bot_response_complete', to=session_id)
    log_and_store_bot_utterance(utterance, participant, dialog_history)


def log_and_store_bot_utterance(utterance, participant, dialog_history):
    utterance_info = {
        'role': 'assistant',
        'content': utterance
    }
    logger.info('utterance', utterance=utterance_info, participant=participant)
    dialog_history.append(utterance_info)
