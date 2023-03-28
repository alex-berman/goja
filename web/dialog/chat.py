import random
from collections import defaultdict
import time

from flask_socketio import emit

from dialog import roles

logger = None
dialog_histories = defaultdict(list)
dialog_start_times = {}


def try_to_pair_with_other_participant(participant, trial):
    def pair_with_other_participant(other_participant_oid):
        pair_oid = insert_pair(ObjectId(participant), other_participant_oid)
        insert_dialog(pair_oid, ObjectId(participant), other_participant_oid)
        pair = db.pairs.find_one({'_id': pair_oid})
        db.participants.update_many(
            {'_id': {'$in': [ObjectId(participant), other_participant_oid]}},
            {'$set': {'state': 'pre_chat'}})
        dialog = db.dialogs.find_one({'pair': pair['_id']})
        ensure_dialog_start_time_is_set(dialog)
        for paired_participant_oid in pair['participants']:
            paired_session_id = db.participants.find_one({'_id': paired_participant_oid})['session_id']
            emit('redirect', {'href': 'participate?participant=' + str(paired_participant_oid)}, to=paired_session_id)

    def insert_pair(participant_oid_0, participant_oid_1):
        paired_participant_oids = [participant_oid_0, participant_oid_1]
        insert_result = db.pairs.insert_one({'participants': paired_participant_oids})
        return insert_result.inserted_id

    def insert_dialog(pair_oid, participant_oid_0, participant_oid_1):
        random_roles = random.sample([roles.OPERATOR, roles.RESPONDENT], 2)
        db.dialogs.insert_one({
            'pair': pair_oid,
            'participants': [
                {'role': random_roles[0], 'participant': participant_oid_0},
                {'role': random_roles[1], 'participant': participant_oid_1}
            ]
        })

    logger.debug('searching for other pairable participant')
    for candidate in db.participants.find(
            {
                '_id': {'$ne': ObjectId(participant)},
                'trial': trial,
                'state': 'pair'
            }):
        logger.debug(f'considering candidate {candidate}')
        other_participant_oid = candidate['_id']
        if not db.pairs.find_one({'participants': other_participant_oid}):
            logger.info(f'found other pairable participant {other_participant_oid}')
            return pair_with_other_participant(other_participant_oid)
    logger.debug('found no other pairable participant')


def ensure_dialog_start_time_is_set(dialog):
    dialog_id = str(dialog['_id'])
    if dialog_id not in dialog_start_times:
        dialog_start_times[dialog_id] = time.time()


def send_history(participant):
    dialog_info = db.dialogs.find_one({'participants.participant': ObjectId(participant)})
    if dialog_info:
        dialog_id = str(dialog_info['_id'])
        for utterance_info in dialog_histories[dialog_id]:
            emit('utterance', utterance_info)


def handle_utterance(role, participant, utterance):
    dialog_info = db.dialogs.find_one({'participants.participant': ObjectId(participant)})
    ensure_dialog_start_time_is_set(dialog_info)
    if dialog_info is None:
        logger.warning('no ongoing dialog')
    else:
        logger.debug('broadcasting to both participants')
        dialog_id = str(dialog_info['_id'])
        time_since_dialog_started = time.time() - dialog_start_times[dialog_id]
        utterance_info = {
            'role': role,
            'utterance': utterance,
            'time': time_since_dialog_started}
        dialog_histories[dialog_id].append(utterance_info)
        for dialog_participant_info in dialog_info['participants']:
            participant_oid = dialog_participant_info['participant']
            participant_info = db.participants.find_one({'_id': participant_oid})
            if participant_info:
                session_id = participant_info['session_id']
                logger.debug(f'emitting utterance to {repr(session_id)}')
                emit('utterance', utterance_info, to=session_id)
            else:
                logger.warning(f'no info found for participant {repr(participant_oid)}')
        return True


def handle_typing(participant, event):
    pair_info = db.pairs.find_one({'participants': ObjectId(participant)})
    if pair_info is None:
        logger.warning('no paired participant')
    else:
        logger.debug('informing other participant about typing event')
        participants_oids = pair_info['participants']
        for candidate_participant_oid in participants_oids:
            candidate_participant = str(candidate_participant_oid)
            if candidate_participant != participant:
                other_participant_info = db.participants.find_one({'_id': candidate_participant_oid})
                if other_participant_info:
                    session_id = other_participant_info['session_id']
                    logger.debug(f'emitting started_typing to {repr(session_id)}')
                    emit('other_typing', {'event': event}, to=session_id)
                else:
                    logger.warning(f'no info found for participant {repr(candidate_participant_oid)}')
