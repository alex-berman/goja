from statemachine import StateMachine, State


class ParticipationStateMachine(StateMachine):
    briefing = State('briefing', initial=True)
    select_case = State('select_case')
    pre_chat_assess = State('pre_chat_assess')
    chat = State('chat')

    proceed = briefing.to(select_case) | select_case.to(pre_chat_assess) | pre_chat_assess.to(chat)


class Model(object):
    def __init__(self, state):
        self.state = state
