from os import getenv
import logging.config

from flask import Flask, request
from flask_socketio import SocketIO
import structlog
import yaml
import pandas as pd
import numpy as np

import participation.participate
from participation.states import ParticipationStateMachine
import dialog.chat
from dialog.bot import Bot
from statemanagement import global_state


cases = None

openai_api_key = getenv('OPENAI_API_KEY')
if openai_api_key is None:
    raise Exception('Please set the OPENAI_API_KEY environment variable')


settings_path = getenv('GOJA_SETUP')
if settings_path is None:
    raise Exception('Please set the GOJA_SETUP environement variable')


settings = participation.participate.settings = yaml.load(open(settings_path), yaml.Loader)
bot = Bot(openai_api_key, settings)
if 'cases' in settings:
    if 'columns' in settings['cases']:
        names = settings['cases']['columns']
    else:
        names = None
    cases = pd.read_csv(settings['cases']['file'], names=names)


logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "default": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.handlers.WatchedFileHandler",
                "filename": "goja.log",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default", "file"],
                "level": "DEBUG",
                "propagate": True,
            },
        }
})
structlog.configure(
    processors=[
        structlog.processors.dict_tracebacks,
        structlog.processors.TimeStamper(fmt="iso", key="ts", utc=False),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


app = Flask(__name__)
logger = dialog.chat.logger = participation.participate.logger = app.logger = structlog.get_logger()
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/dev/status', methods=['GET'])
def status():
    return 'OK'


@app.route("/", methods=['POST', 'GET'])
def participate():
    return participation.participate.participate(request)


@socketio.on('start')
def start():
    logger.info('start')
    participant_id = participation.participate.create_participant_id()
    logger.info('add_participant', participant=participant_id)
    participant_info = {
        'state': ParticipationStateMachine().current_state.name,
        'dialog_histories': [],
        'assessments': {
            'assess_without_bot': {},
            'assess_with_bot': {},
        }
    }
    if cases is not None:
        num_cases = settings['cases']['n']
        case_indexes_without_bot = np.random.choice(len(cases.index), size=num_cases, replace=False)
        case_indexes_with_bot = np.random.choice(case_indexes_without_bot, size=num_cases, replace=False)
        participant_info['shuffled_case_indexes'] = {
            'assess_without_bot': case_indexes_without_bot,
            'assess_with_bot': case_indexes_with_bot,
        }
        participant_info['case_count'] = 0
    global_state.participants[participant_id] = participant_info
    return participant_id


@socketio.on('proceed')
def proceed(payload):
    logger.info('proceed', payload=payload)
    participant = payload['participant']
    global_state.participants[participant]['session_id'] = request.sid
    return participation.participate.proceed(participant, cases, request.sid)


@socketio.on('request_content')
def handle_request_for_content(payload):
    logger.info('request_content', payload=payload)
    participant = payload['participant']
    global_state.participants[participant]['session_id'] = request.sid
    return participation.participate.handle_request_for_content(participant)


@socketio.on('update_session')
def update_session(payload):
    logger.info('update_session', payload=payload)
    participant = payload['participant']
    global_state.participants[participant]['session_id'] = request.sid


@socketio.on('request_chat_history')
def request_chat_history(payload):
    logger.info('request_chat_history', payload=payload)
    participant = payload['participant']
    dialog.chat.send_history(participant)


@socketio.on('utter')
def handle_utterance(payload):
    logger.info('utter', payload=payload)
    participant = payload['participant']
    utterance = payload['utterance']
    return dialog.chat.handle_utterance(participant, utterance, bot, socketio)


@socketio.on('get_state')
def update_session(payload):
    logger.info('get_state', payload=payload)
    participant = payload['participant']
    socketio.emit('state', global_state.participants[participant]['state'], to=request.sid)


@socketio.on('get_case')
def get_case(payload):
    logger.info('get_case', payload=payload)
    participant = payload['participant']
    send_case(participant, request.sid)


def send_case(participant, session_id):
    participant_info = global_state.participants[participant]
    state = participant_info['state']
    if state in participant_info['assessments']:
        case_count = participant_info['case_count']
        case_index = participant_info['shuffled_case_indexes'][state][case_count]
        case = cases.iloc[case_index]
        assessments = participant_info['assessments'][state]
        if case_index in assessments:
            assessment = assessments[case_index]
        else:
            assessment = None
        payload = {
            'state': state,
            'count': case_count + 1,
            'index': int(case_index),
            'features': case.to_dict(),
            'assessment': assessment
        }
        logger.debug("emit case", payload=payload)
        socketio.emit('case', payload, to=session_id)
    else:
        logger.debug("no assessments found", state=state)


@socketio.on('update_assessment')
def update_assessment(payload):
    logger.info('update_assessment', payload=payload)
    participant = payload['participant']
    label = payload['assessment']
    state = payload['state']
    participant_info = global_state.participants[participant]
    case_count = participant_info['case_count']
    case_index = participant_info['shuffled_case_indexes'][state][case_count]
    assessments =  participant_info['assessments'][state]
    assessments[case_index] = label
    send_case(participant, request.sid)


@socketio.on('proceed_within_cases')
def proceed_within_cases(payload):
    logger.info('proceed_within_cases', payload=payload)
    participant = payload['participant']
    case_count = global_state.participants[participant]['case_count']
    new_case_count = case_count + payload['step']
    if new_case_count >= settings['cases']['n']:
        participation.participate.proceed(participant, cases, request.sid)
        global_state.participants[participant]['case_count'] = 0
    else:
        if new_case_count < 0:
            new_case_count = 0
        global_state.participants[participant]['case_count'] = new_case_count
        send_case(participant, request.sid)


@socketio.on('restart_chat')
def restart_chat(payload):
    logger.info('restart_chat', payload=payload)
    participant = payload['participant']
    participation.participate.initialize_chat(participant)
    dialog.chat.send_history(participant)


if __name__ == '__main__':
    socketio.run(app, host=args.host, port=args.port)
