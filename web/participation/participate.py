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


def participate(request, settings):
    participant = request.args.get('participant')
    if participant:
        current_state = global_state.participants[participant]['state']
        if current_state in ['pre_chat_assess', 'chat']:
            return interact(participant, settings)

    template = env.get_template('general.html')
    return template.render(participant=participant, url_for=url_for)


def proceed(participant, cases, session_id):
    current_state = global_state.participants[participant]['state']
    logger.info(f'current state: {current_state}')
    state_machine = ParticipationStateMachine(Model(current_state))
    state_machine.proceed()
    new_state = state_machine.current_state.name
    if new_state == 'select_case':
        if cases is None:
            new_state = 'chat'
        else:
            case_index = global_state.participants[participant]['shuffled_case_indexes'][
                global_state.participants[participant]['case_count']]
            case = cases.iloc[case_index]
            logger.info('case', {'participant': participant, 'case': case.to_dict()})
            new_state = 'pre_chat_assess'
    logger.info(f'state after proceeding: {new_state}')
    global_state.participants[participant]['state'] = new_state
    send_update_to_client(participant, new_state)


def send_update_to_client(participant, state):
    if state in ['pre_chat_assess', 'chat']:
        emit('redirect', {'href': '?participant=' + participant})
    else:
        template = env.get_template('content.html')
        content = template.render(state=state)
        emit('content', content)


def handle_request_for_content(participant):
    current_state = global_state.participants[participant]['state']
    logger.info(f'current state: {current_state}')
    send_update_to_client(participant, current_state)


def interact(participant, settings):
    template = env.get_template('interact.html')
    cases_enabled = settings['cases'] is not None

    extra_head_js = ''
    if 'frontend_javascript' in settings:
        extra_head_js += f'<script src="{settings["frontend_javascript"]}"></script>\n'
    if 'frontend_css' in settings:
        extra_head_js += f'<link rel="stylesheet" href="{settings["frontend_css"]}">\n'

    return template.render(
        participant=participant,
        cases_enabled=cases_enabled,
        extra_head_js=extra_head_js,
        settings=settings)
