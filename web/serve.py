import json
import argparse
from os import getenv
import pathlib

import flask
from flask import Flask, request
from flask_socketio import SocketIO

import participation.participate
import dialog.chat


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
    result = db.participants.insert_one({'session_id': request.sid, 'state': 'pre_rate'})
    participant = str(result.inserted_id)
    return participant


@socketio.on('proceed')
def proceed(json):
    logger.info(f'proceed {json}')
    participant = json['participant']
    db.participants.update_one(
        {'_id': ObjectId(participant)},
        {'$set': {'session_id': request.sid}})
    return participation.participate.proceed(participant, request.sid, trial, db)


@socketio.on('request_content')
def handle_request_for_content(json):
    logger.info(f'request_content {json}')
    participant = json['participant']
    db.participants.update_one(
        {'_id': ObjectId(participant)},
        {'$set': {'session_id': request.sid}})
    return participation.participate.handle_request_for_content(participant, db)


@socketio.on('update_session')
def update_session(json):
    logger.info(f'update_session {json}')
    participant = json['participant']
    db.participants.update_one(
        {'_id': ObjectId(participant)},
        {'$set': {'session_id': request.sid}})


@socketio.on('request_chat_history')
def request_chat_history(json):
    logger.info(f'request_chat_history {json}')
    participant = json['participant']
    dialog.chat.send_history(participant)


@socketio.on('utter')
def handle_utterance(json):
    logger.info('handle_utterance: ' + str(json))
    role = json['role']
    participant = json['participant']
    utterance = json['utterance']
    return dialog.chat.handle_utterance(role, participant, utterance)


@socketio.on('typing')
def handle_typing(json):
    logger.info('handle_started_typing: ' + str(json))
    participant = json['participant']
    event = json['event']
    return dialog.chat.handle_typing(participant, event)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port')
    parser.add_argument('--host')
    args = parser.parse_args()
    socketio.run(app, host=args.host, port=args.port)
