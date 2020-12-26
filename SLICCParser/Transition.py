import Action
class Transition(object):
    current_state = 0
    next_state = 0
    action = 0
    def __init__(self, action):
        self.action = action
    
    def getNextState(self, event,current_state, transition_table):
        current_state = current_state
        next_state = transition_table.loc[[current_state][event]]
