import uuid

from jinja2 import Environment, PackageLoader
from flask import url_for
from flask_socketio import emit

from participation.states import ParticipationStateMachine, Model
import dialog.chat
from statemanagement import global_state


env = Environment(loader=PackageLoader('participation.participate'))
settings = None
logger = None


def create_participant_id():
    return str(uuid.uuid4())


def participate(request):
    participant = request.args.get('participant')
    if participant:
        current_state = global_state.participants[participant]['state']
        if current_state in ['assess_without_bot', 'assess_with_bot']:
            logger.info('returning interaction page')
            return interact(participant)

    logger.info('returning information page')
    template = env.get_template('general.html')
    return template.render(participant=participant, settings=settings, url_for=url_for)


def proceed(participant, cases, session_id):
    current_state = global_state.participants[participant]['state']
    logger.info(f'current state: {current_state}')
    state_machine = ParticipationStateMachine(Model(current_state))
    state_machine.proceed()
    new_state = state_machine.current_state.name
    logger.info(f'state after proceeding: {new_state}')
    global_state.participants[participant]['state'] = new_state
    if new_state == 'assess_with_bot':
        initialize_chat(participant)
    send_update_to_client(participant, new_state)


def initialize_chat(participant):
    participant_info = global_state.participants[participant]
    if 'initial_assistant_utterance' in settings:
        dialog.chat.log_and_store_bot_utterance(
            settings['initial_assistant_utterance'], participant, participant_info['dialog_history'])


def send_update_to_client(participant, state):
    if state in ['assess_without_bot', 'before_assess_with_bot', 'assess_with_bot', 'debriefing']:
        logger.info('emitting redirect')
        emit('redirect', {'href': '?participant=' + participant})
    else:
        send_content_to_client(participant, state)


def send_content_to_client(participant, state):
    logger.info('emitting content')
    content = settings['state_specific_info'][state]
    emit('content', content)


def handle_request_for_content(participant):
    state = global_state.participants[participant]['state']
    logger.info(f'current state: {state}')
    send_content_to_client(participant, state)


def interact(participant):
    template = env.get_template('interact.html')
    cases_enabled = settings['cases'] is not None
    state = global_state.participants[participant]['state']
    print('state='); print(state)

    extra_head_js = ''
    if 'frontend_javascript' in settings:
        extra_head_js += f'<script src="{settings["frontend_javascript"]}"></script>\n'
    if 'frontend_css' in settings:
        extra_head_js += f'<link rel="stylesheet" href="{settings["frontend_css"]}">\n'

    return template.render(
        participant=participant,
        state=state,
        cases_enabled=cases_enabled,
        extra_head_js=extra_head_js,
        settings=settings)
