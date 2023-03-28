from jinja2 import Environment, PackageLoader
from flask import url_for
from flask_socketio import emit

from dialog import roles
from participation.states import ParticipationStateMachine, Model
import dialog.chat


env = Environment(loader=PackageLoader('participation.participate'))


def participate(request):
    participant = request.args.get('participant')
    if participant:
        current_state = db.participants.find_one({'_id': ObjectId(participant)})['state']
        if current_state == 'chat':
            role = get_dialog_role(participant, db)
            return chat(participant, role, db)

    template = env.get_template('general.html')
    return template.render(participant=participant, url_for=url_for)


def get_dialog_role(participant, db):
    dialog_info = db.dialogs.find_one({'participants.participant': ObjectId(participant)})
    if dialog_info:
        for dialog_participant_info in dialog_info['participants']:
            if dialog_participant_info['participant'] == ObjectId(participant):
                return dialog_participant_info['role']


def proceed(participant, session_id, trial, db):
    current_state = db.participants.find_one({'_id': ObjectId(participant)})['state']
    logger.info(f'current state: {current_state}')
    state_machine = ParticipationStateMachine(Model(current_state))
    state_machine.proceed()
    new_state = state_machine.current_state.name
    logger.info(f'state after proceeding: {new_state}')
    db.participants.update_one(
        {'_id': ObjectId(participant)},
        {'$set': {'state': new_state}})
    send_update_to_client(participant, new_state, db)
    if new_state == 'pair':
        dialog.chat.try_to_pair_with_other_participant(participant, trial)


def send_update_to_client(participant, state, db):
    if state == 'rate':
        emit('redirect', {'href': 'rate?participant=' + participant})
    elif state == 'chat':
        emit('redirect', {'href': 'participate?participant=' + participant})
    else:
        role = get_dialog_role(participant, db)
        template = env.get_template('content.html')
        content = template.render(state=state, role=role)
        emit('content', content)


def handle_request_for_content(participant, db):
    current_state = db.participants.find_one({'_id': ObjectId(participant)})['state']
    logger.info(f'current state: {current_state}')
    send_update_to_client(participant, current_state, db)


def chat(participant, role, db):
    template = env.get_template('chat.html')
    return template.render(participant=participant)


def get_paired_participant(participant, db):
    pair_info = db.pairs.find_one({'participants': ObjectId(participant)})
    if pair_info is None:
        raise Exception(f'Failed to find a pair for participant {repr(participant)}')
    paired_participants_set = set([str(oid) for oid in pair_info['participants']])
    paired_participants_set.remove(participant)
    other_participant = list(paired_participants_set)[0]
    return other_participant
