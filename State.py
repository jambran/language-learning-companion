from random import choice

class State(object):
    def __init__(self, name, production, transitions):
        self.name = name
        self.production = production
        self.transitions = transitions
    def choose_transition(self):
        return choice(self.transitions)