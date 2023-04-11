from statemachine import StateMachine, State


class ParticipationStateMachine(StateMachine):
    briefing = State('briefing', initial=True)
    before_assess_without_bot = State('before_assess_without_bot')
    assess_without_bot = State('assess_without_bot')
    before_assess_with_bot = State('before_assess_with_bot')
    assess_with_bot = State('assess_with_bot')
    debriefing = State('debriefing')

    proceed = \
        briefing.to(before_assess_without_bot) | \
        before_assess_without_bot.to(assess_without_bot) | \
        assess_without_bot.to(before_assess_with_bot) | \
        before_assess_with_bot.to(assess_with_bot) | \
        assess_with_bot.to(debriefing)


class Model(object):
    def __init__(self, state):
        self.state = state
