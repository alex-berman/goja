from statemachine import StateMachine, State


class ParticipationStateMachine(StateMachine):
    pre_chat = State('pre_chat', initial=True)
    chat = State('chat')

    proceed = pre_chat.to(chat)


class Model(object):
    def __init__(self, state):
        self.state = state
