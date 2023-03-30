import uuid

from jinja2 import Environment, PackageLoader
from flask import url_for
from flask_socketio import emit

from participation.states import ParticipationStateMachine, Model
import dialog.chat
from statemanagement import global_state


env = Environment(loader=PackageLoader('participation.participate'))


def create_participant_id():
    return str(uuid.uuid4())


def participate(request):
    participant = request.args.get('participant')
    if participant:
        current_state = global_state.participants[participant]['state']
        if current_state == 'chat':
            return chat(participant)

    template = env.get_template('general.html')
    return template.render(participant=participant, url_for=url_for)


def proceed(participant, session_id):
    current_state = global_state.participants[participant]['state']
    logger.info(f'current state: {current_state}')
    state_machine = ParticipationStateMachine(Model(current_state))
    state_machine.proceed()
    new_state = state_machine.current_state.name
    logger.info(f'state after proceeding: {new_state}')
    global_state.participants[participant]['state'] = new_state
    send_update_to_client(participant, new_state)


def send_update_to_client(participant, state):
    if state == 'chat':
        emit('redirect', {'href': '?participant=' + participant})
    else:
        template = env.get_template('content.html')
        content = template.render(state=state)
        emit('content', content)


def handle_request_for_content(participant):
    current_state = global_state.participants[participant]['state']
    logger.info(f'current state: {current_state}')
    send_update_to_client(participant, current_state)


def chat(participant):
    template = env.get_template('chat.html')
    return template.render(participant=participant)
