from otree.api import *

doc = """
Instructions and consent
"""


class C(BaseConstants):
    NAME_IN_URL = 'instructions_consent'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    TOTAL_DURATION = 80
    AVG_ADD_INCOME = cu(7.0)  # average extra income they can earn from the tasks
    BELIEF_BONUS = 666.67  # bonus for correct beliefs
    SCALING_PAR = 900
    FLAT_LEISURE_FEE = 66.67  # flat fee per minute of leisure
    BENEFIT_RANGE_MIN = 50
    BENEFIT_RANGE_MAX = 150
    TRUE_PAYOFF = 120
    PERCENT_IDEAL = 3  # percentage chance that they will have to do the ideal number of tasks


# Solutions for comprehension check
solutions = dict(
    q1='Yes, because each ball is shown only once, and by part 4 all 120 have been shown.',
    q2='It will be based on your performance in a randomly chosen part (trial or one of the five main parts).',
    q3=30,
    q4='State your actual belief about the true payoff, because the closer your guess is to the real value (between 50 points and 150 points), the higher your probability of winning.',
    q5='It is the average of 120 numbers between 50 points and 150 points.'
)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Consent
    consent = models.BooleanField(label="Do you wish to participate in the study?", initial=False)

    # comprehension check answers
    q1 = models.StringField(
        label='<b>Question 1</b> <br> At the end of part 4, will you have seen all the numbers (“balls”) from the underlying distribution?',
        choices=[
            'Yes, because the same 120 balls are shown repeatedly in every part.',
            'Yes, because each ball is shown only once, and by part 4 all 120 have been shown.',
            'No, because some balls are never shown.',
        ],
        widget=widgets.RadioSelect,
    )

    q2 = models.StringField(
        label='<b>Question 2</b> <br> Which of the following correctly describes how your payoff from the encryption task will be determined?',
        choices=[
            'It will always be based on your performance in the final part of the study.',
            'It will be based on your performance in a randomly chosen part (trial or one of the five main parts).',
            'It will be based on your average performance across all parts.',
        ],
        widget=widgets.RadioSelect,
    )

    q3 = models.IntegerField(
        label='<b>Question 3</b> <br> In each of the first four parts, how many balls will you see at the beginning of the part?'
    )

    q4 = models.StringField(
        label='<b>Question 4</b> <br> When guessing the fixed payoff per task, how should you choose your guess to maximize your chance of winning the extra payment?',
        choices=[
            'Always guess a very high number.',
            'State your actual belief about the true payoff, because the closer your guess is to the real value (between 50 points and 150 points), the higher your probability of winning.',
            'Always guess the middle value between 50 points and 150 points.',
        ],
        widget=widgets.RadioSelect,
    )

    q5 = models.StringField(
        label='<b>Question 5</b> <br> How is the fixed payoff per correctly solved task calculated?',
        choices=[
            'It is the average of 120 numbers between 50 points and 150 points.',
            'It is the highest number out of the 120 balls shown.',
            'It is a random number chosen between 50 and 150 each round.',
        ],
        widget=widgets.RadioSelect,
    )

    attempt_number = models.IntegerField(initial=0)
    num_wrong = models.IntegerField(initial=0)
    wrong_questions = models.StringField(initial="")
    success_attempt = models.IntegerField(initial=None)
    excluded = models.BooleanField(initial=False)


def creating_session(subsession: Subsession):
    # define participant variables
    for p in subsession.get_players():
        p.participant.vars['consent'] = False
        p.participant.vars['total_wrong'] = None
        p.participant.vars['success_attempt'] = None
        p.participant.vars['attempt_number'] = 0
        p.participant.vars['excluded'] = False

        print('Participant variables are', p.participant.vars)


# PAGES
class Welcome(Page):
    pass


class EncryptionTask(Page):
    pass


class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        participation_fee = player.session.config['participation_fee']
        return dict(
            participation_fee=participation_fee
        )


class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5']

    @staticmethod
    def is_displayed(player):
        success = player.field_maybe_none('success_attempt')
        return (not player.excluded) and (success is None or success == 0)

    @staticmethod
    def vars_for_template(player):
        # split wrong_questions into a list, handle None
        wrong_questions_list = player.wrong_questions.split(',') if player.wrong_questions else []
        participation_fee = player.session.config['participation_fee']
        return dict(
            attempt_number=player.attempt_number,
            wrong_questions_list=wrong_questions_list,
            participation_fee=participation_fee
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Increment attempt number
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

        # Exclusion / success logic
        if player.num_wrong >= 4:
            player.excluded = True  # immediately exclude
            player.success_attempt = None
        elif player.num_wrong == 0:
            player.success_attempt = player.attempt_number
        else:
            player.success_attempt = 0  # allow second attempt

        player.participant.vars['success_attempt'] = player.success_attempt
        player.participant.vars['attempt_number'] = player.attempt_number
        player.participant.vars['excluded'] = player.excluded

        if player.participant.vars['total_wrong'] is None:
            player.participant.vars['total_wrong'] = 0
        player.participant.vars['total_wrong'] += player.num_wrong


class ShowCorrectAnswers(Page):
    @staticmethod
    def is_displayed(player):
        # Show correct answers only if they failed twice but are not excluded
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
    ComprehensionCheck,
    ShowCorrectAnswers,
    Excluded,
    Consent,
    NoConsent,
]
