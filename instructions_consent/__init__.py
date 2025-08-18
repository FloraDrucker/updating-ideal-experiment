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
    PERCENT_IDEAL = 3  # percentage chance that they will have to do the ideal number of tasks

# Solutions for comprehension check
solutions = dict(
    q1='Yes, because each ball is shown only once, and by part 4 all 120 have been shown',
    q2='It will be based on your performance in a randomly chosen part (trial or one of the five main parts)',
    q3=30,
    q4='State your actual belief about the true payoff, because the closer your guess is to the real value (between 50¢ and 150¢), the higher your probability of winning',
    q5='It is the average of 120 numbers between 50¢ and 150¢'
)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Consent
    consent = models.BooleanField(label="Do you wish to participate in the study?")

    # comprehension check answers
    q1 = models.StringField(
        label='At the end of part 4, will you have seen all the numbers (“balls”) from the underlying distribution?',
        choices=[
            'Yes, because the same 120 balls are shown repeatedly in every part',
            'Yes, because each ball is shown only once, and by part 4 all 120 have been shown',
            'No, because some balls are never shown',
        ],
        widget=widgets.RadioSelect,
    )

    q2 = models.StringField(
        label='Which of the following correctly describes how your payoff from the encryption task will be determined?',
        choices=[
            'It will always be based on your performance in the final part of the study',
            'It will be based on your performance in a randomly chosen part (trial or one of the five main parts)',
            'It will be based on your average performance across all parts',
        ],
        widget=widgets.RadioSelect,
    )

    q3 = models.IntegerField(
        label='In each of the first four parts, how many balls will you see at the beginning of the part?'
    )

    q4 = models.StringField(
        label='When guessing the fixed payoff per task, how should you choose your guess to maximize your chance of winning the extra payment?',
        choices=[
            'Always guess a very high number',
            'State your actual belief about the true payoff, because the closer your guess is to the real value (between 50¢ and 150¢), the higher your probability of winning',
            'Always guess the middle value between 50¢ and 150¢',
        ],
        widget=widgets.RadioSelect,
    )

    q5 = models.StringField(
        label='How is the fixed payoff per correctly solved task calculated?',
        choices=[
            'It is the average of 120 numbers between 50¢ and 150¢',
            'It is the highest number out of the 120 balls shown',
            'It is a random number chosen between 50¢ and 150¢ each round',
        ],
        widget=widgets.RadioSelect,
    )

    attempt_number = models.IntegerField(initial=0)
    num_wrong = models.IntegerField(initial=0)
    wrong_questions = models.StringField(blank=True)
    success_attempt = models.IntegerField(initial=None)  # which try got correct
    excluded = models.BooleanField(initial=False)


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

class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.attempt_number += 1

        # Check which questions are wrong
        wrong_list = []
        if player.q1 != solutions['q1']:
            wrong_list.append('q1')
        if player.q2 != solutions['q2']:
            wrong_list.append('q2')
        if player.q3 != solutions['q3']:
            wrong_list.append('q3')
        if player.q4 != solutions['q4']:
            wrong_list.append('q4')
        if player.q5 != solutions['q5']:
            wrong_list.append('q5')

        player.num_wrong = len(wrong_list)
        player.wrong_questions = ','.join(wrong_list)

        # Exclusion logic
        if player.num_wrong >= 4:
            player.excluded = True
        elif player.num_wrong == 0:
            player.success_attempt = player.attempt_number
        # Else, leave success_attempt=0 to allow second attempt

class ShowWrongAnswers(Page):
    @staticmethod
    def is_displayed(player):
        return player.attempt_number == 1 and 0 < player.num_wrong <= 3

    @staticmethod
    def vars_for_template(player):
        return dict(
            wrong_questions_list=player.wrong_questions.split(',') if player.wrong_questions else []
        )

class ShowCorrectAnswers(Page):
    @staticmethod
    def is_displayed(player):
        return player.attempt_number == 2 and player.success_attempt == 0 and not player.excluded

    @staticmethod
    def vars_for_template(player):
        return dict(solutions=solutions)


class Excluded(Page):
    @staticmethod
    def is_displayed(player):
        return player.excluded

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vars['consent'] = player.consent
        print("Participant:", player.participant.code, "Variables:", player.participant.vars)

class NoConsent(Page):
    @staticmethod
    def is_displayed(player):
        return player.consent is not None and player.consent is False

page_sequence = [
    Welcome,
    EncryptionTask,
    Instructions,
    ComprehensionCheck,
    ShowCorrectAnswers,
    Excluded,
    Consent,
    NoConsent,
]
