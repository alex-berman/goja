import json
import argparse
from os import getenv
import pathlib

import flask
from flask import Flask, request
from flask_socketio import SocketIO

import participation.participate
from participation.states import ParticipationStateMachine
import dialog.chat
from dialog.bot import Bot
from statemanagement import global_state


app = Flask(__name__)
logger = dialog.chat.logger = participation.participate.logger = app.logger
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

@app.route('/dev/status', methods=['GET'])
def status():
    return 'OK'


@app.route("/participate", methods=['POST', 'GET'])
def participate():
    return participation.participate.participate(request)


@socketio.on('start')
def start():
    logger.info(f'start')
    participant = participation.participate.create_participant_id()
    global_state.participants[participant] = {
        'state': ParticipationStateMachine().current_state.name,
        'dialog_history': []
    }
    return participant


@socketio.on('proceed')
def proceed(json):
    logger.info(f'proceed {json}')
    participant = json['participant']
    global_state.participants[participant]['session_id'] = request.sid
    return participation.participate.proceed(participant, request.sid)


@socketio.on('request_content')
def handle_request_for_content(json):
    logger.info(f'request_content {json}')
    participant = json['participant']
    global_state.participants[participant]['session_id'] = request.sid
    return participation.participate.handle_request_for_content(participant)


@socketio.on('update_session')
def update_session(json):
    logger.info(f'update_session {json}')
    participant = json['participant']
    global_state.participants[participant]['session_id'] = request.sid


@socketio.on('request_chat_history')
def request_chat_history(json):
    logger.info(f'request_chat_history {json}')
    participant = json['participant']
    dialog.chat.send_history(participant)


@socketio.on('utter')
def handle_utterance(json):
    logger.info('handle_utterance: ' + str(json))
    participant = json['participant']
    utterance = json['utterance']
    return dialog.chat.handle_utterance(participant, utterance, bot, socketio)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('settings', help='path to YAML file with settings')
    parser.add_argument('--port')
    parser.add_argument('--host')
    args = parser.parse_args()
    bot = Bot(getenv('OPENAI_API_KEY'), args.settings)
    socketio.run(app, host=args.host, port=args.port)
