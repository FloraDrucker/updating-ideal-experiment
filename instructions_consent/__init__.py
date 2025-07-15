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
    BENEFIT_RANGE_MIN = 50
    BENEFIT_RANGE_MAX = 150
    PERCENT_IDEAL = 100  # percentage chance that they will have to do the ideal number of tasks


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField(label="Do you wish to participate in the study?")


def creating_session(subsession: Subsession):
    # define participant variables
    for p in subsession.get_players():
        p.participant.vars['consent'] = None


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

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vars['consent'] = player.consent
        print("Participant:", player.participant.code, "Variables:", player.participant.vars)


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
