import argparse
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('settings', help='path to YAML file with settings')
    parser.add_argument('--log', default='goja.log')
    parser.add_argument('--port')
    parser.add_argument('--host')
    args = parser.parse_args()
    openai_api_key = getenv('OPENAI_API_KEY')
    if openai_api_key is None:
        raise Exception('Please set the OPENAI_API_KEY environment variable')
    settings = yaml.load(open(args.settings), yaml.Loader)
    bot = Bot(openai_api_key, settings)
    if 'cases' in settings:
        cases = pd.read_csv(settings['cases'])


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
                "filename": args.log,
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
    participant = participation.participate.create_participant_id()
    logger.info('add_participant', participant=participant)
    global_state.participants[participant] = {
        'state': ParticipationStateMachine().current_state.name,
        'dialog_history': []
    }
    if cases is not None:
        num_cases = len(cases.index)
        global_state.participants[participant]['shuffled_case_indexes'] = np.random.choice(num_cases, size=num_cases)
        global_state.participants[participant]['case_count'] = 0
    return participant


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


if __name__ == '__main__':
    socketio.run(app, host=args.host, port=args.port)
