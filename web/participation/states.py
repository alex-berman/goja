from statemachine import StateMachine, State


class ParticipationStateMachine(StateMachine):
    pre_rate = State('pre_rate', initial=True)
    rate = State('rate')
    pre_pair = State('pre_pair')
    pair = State('pair')
    pre_chat = State('pre_chat')
    chat = State('chat')

    proceed = pre_rate.to(rate) | rate.to(pre_pair) | pre_pair.to(pair) | pair.to(pre_chat) | pre_chat.to(chat)
    paired = pair.to(chat)


class Model(object):
    def __init__(self, state):
        self.state = state
