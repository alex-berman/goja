OPERATOR = 'operator'
RESPONDENT = 'respondent'


def other(role):
    if role == OPERATOR:
        return RESPONDENT
    if role == RESPONDENT:
        return OPERATOR
