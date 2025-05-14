from otree.api import *


doc = """
Instructions and consent
"""


class C(BaseConstants):
    NAME_IN_URL = 'instructions_consent'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    TOTAL_DURATION = 80
    AVG_ADD_INCOME = cu(5.0)  # average extra income they can earn from the tasks
    BELIEF_BONUS = cu(2.0)  # bonus for correct beliefs
    SCALING_PAR = 25  # TODO: change this!! scaling parameter for the binarized quadratic scoring rule


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField(label="Do you wish to participate in the study?")


# PAGES
class Welcome(Page):
    pass


class EncryptionTask(Page):
    pass


class Instructions(Page):
    pass


class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']


class NoConsent(Page):
    def is_displayed(player):
        return player.consent is False
    pass


page_sequence = [
    Welcome,
    EncryptionTask,
    Instructions,
    Consent,
    NoConsent
]
