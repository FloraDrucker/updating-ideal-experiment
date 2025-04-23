from otree.api import *


doc = """
Instructions and consent
"""


class C(BaseConstants):
    NAME_IN_URL = 'instructions_consent'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class Welcome(Page):
    pass


class SessionZero(Page):
    pass


page_sequence = [Welcome, SessionZero]
