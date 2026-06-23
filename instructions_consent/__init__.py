from otree.api import *

doc = """
Instructions and consent
"""


class C(BaseConstants):
    NAME_IN_URL = 'instructions_consent'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    TOTAL_DURATION = 75
    AVG_ADD_INCOME = cu(5.7)  # average extra income they can earn from the tasks
    BELIEF_BONUS = 670  # bonus for correct beliefs
    SCALING_PAR = 900
    FLAT_LEISURE_FEE = 70  # flat fee per minute of leisure
    BENEFIT_RANGE_MIN = 50
    BENEFIT_RANGE_MAX = 150
    TRUE_PAYOFF = 120
    PERCENT_IDEAL = 2  # percentage chance that they will have to do the ideal number of tasks
    GUESS_ABOUT = {True: "payoff per task",
                   False: "chosen number"}
    # Solutions for comprehension check
    SOLUTIONS = dict(
        q1='Yes, because each ball is shown only once, and by part four all 60 will have been shown.',
        q2='It will be based on your performance in a randomly chosen part (trial or one of the five main parts).',
        q3=20,
        q4c='State your actual belief about the chosen number, because the closer your guess is to the real value (between 50 points and 150 points), the higher is your probability of winning.',
        q4t='State your actual belief about the true payoff, because the closer your guess is to the real value (between 50 points and 150 points), the higher is your probability of winning.',
        q5c='It is the average of 60 numbers between 50 and 150.',
        q5t='It is the average of 60 numbers between 50 points and 150 points.'
    )


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Treatment
    treatment = models.BooleanField(blank=False)

    # Consent
    consent = models.BooleanField(label="Do you wish to participate in the study?", blank=False)

    # comprehension check answers
    q1 = models.StringField(
        label='<b>Question 1</b> <br> At the end of part four, will you have seen all the numbers (“balls”) from the underlying distribution?',
        choices=[
            'Yes, because the same 60 balls are shown repeatedly in every part.',
            'Yes, because each ball is shown only once, and by part four all 60 will have been shown.',
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
        label='<b>Question 3</b> <br> In each of the second, third and fourth parts, how many balls will you see at the beginning of the part?'
    )

    q4t = models.StringField(
        label='<b>Question 4</b> <br> When guessing the fixed payoff per task, how should you choose your guess to maximize your chance of winning the extra payment?',
        choices=[
            'Always guess a very high number.',
            'State your actual belief about the true payoff, because the closer your guess is to the real value (between 50 points and 150 points), the higher is your probability of winning.',
            'Always guess the middle value between 50 points and 150 points.',
        ],
        widget=widgets.RadioSelect,
    )

    q4c = models.StringField(
        label='<b>Question 4</b> <br> When guessing the chosen number, how should you choose your guess to maximize your chance of winning the extra payment?',
        choices=[
            'Always guess a very high number.',
            'State your actual belief about the chosen number, because the closer your guess is to the real value (between 50 points and 150 points), the higher is your probability of winning.',
            'Always guess the middle value between 50 points and 150 points.',
        ],
        widget=widgets.RadioSelect,
    )

    q5t = models.StringField(
        label='<b>Question 5</b> <br> How is the fixed payoff per correctly solved task calculated?',
        choices=[
            'It is the average of 60 numbers between 50 points and 150 points.',
            'It is the highest number out of the 60 balls shown.',
            'It is a random number chosen between 50 and 150 each round.',
        ],
        widget=widgets.RadioSelect,
    )

    q5c = models.StringField(
        label='<b>Question 5</b> <br> How is the chosen number calculated?',
        choices=[
            'It is the average of 60 numbers between 50 and 150.',
            'It is the highest number out of the 60 balls shown.',
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
    import itertools
    treatments = itertools.cycle([True, False]) # False = Control, True = Main
    config = subsession.session.config

    # define treatment and participant variables
    for p in subsession.get_players():
        if config['set_treatment'] is False:
            p.treatment = next(treatments)
        else:
            p.treatment = config['treatment']
        p.participant.vars['treatment'] = p.treatment
        p.participant.vars['consent'] = False
        p.participant.vars['total_wrong'] = None
        p.participant.vars['success_attempt'] = None
        p.participant.vars['attempt_number'] = 0
        p.participant.vars['excluded'] = False
        p.participant.vars['wrong_questions_attempt1'] = ""
        p.participant.vars['wrong_questions_attempt2'] = ""

def page_timeout(timeout_key):
    def get_timeout_seconds(player):
        return player.session.config['page_timeouts'][timeout_key]

    return staticmethod(get_timeout_seconds)


def exclude_on_incomplete_timeout(
    player, timeout_happened, required_fields, page_name
):
    """Exclude when a timed form is submitted with required answers missing."""
    if not timeout_happened:
        return False

    missing_fields = [
        field_name
        for field_name in required_fields
        if player.field_maybe_none(field_name) is None
    ]
    if not missing_fields:
        return False

    player.excluded = True
    ppvars = player.participant.vars
    ppvars['excluded'] = True
    ppvars['exclusion_reason'] = 'incomplete_timeout'
    ppvars['exclusion_page'] = page_name
    ppvars['missing_fields_at_timeout'] = missing_fields
    return True


# PAGES
class Welcome(Page):
    get_timeout_seconds = page_timeout('welcome')


class EncryptionTask(Page):
    get_timeout_seconds = page_timeout('encryption_task')


class Instructions(Page):
    get_timeout_seconds = page_timeout('instructions')

    @staticmethod
    def vars_for_template(player: Player):
        participation_fee = player.session.config['participation_fee']
        thousand_points = cu(player.session.config['real_world_currency_per_point']*1000)
        guess_about = C.GUESS_ABOUT[player.treatment]
        percent_normal = 100 - C.PERCENT_IDEAL
        return dict(
            participation_fee=participation_fee,
            thousand_points=thousand_points,
            guess_about=guess_about,
            percent_normal=percent_normal,
        )


class ComprehensionCheck(Page):
    get_timeout_seconds = page_timeout('comprehension_check')

    form_model = 'player'
    # oTree normally converts missing timeout answers to '', 0, or False.
    # Keeping them as None lets before_next_page distinguish them from real answers.
    timeout_submission = {
        'q1': None,
        'q2': None,
        'q3': None,
        'q4t': None,
        'q4c': None,
        'q5t': None,
        'q5c': None,
    }

    @staticmethod
    def get_form_fields(player):
        if player.treatment:
            return ['q1', 'q2', 'q3', 'q4t', 'q5t']
        else:
            return ['q1', 'q2', 'q3', 'q4c', 'q5c']

    @staticmethod
    def is_displayed(player):
        success = player.field_maybe_none('success_attempt')
        return (not player.excluded) and (success is None or success == 0)

    @staticmethod
    def vars_for_template(player):
        # split wrong_questions into a list, handle None
        wrong_questions_list = player.wrong_questions.split(',') if player.wrong_questions else []
        participation_fee = player.session.config['participation_fee']
        thousand_points = cu(player.session.config['real_world_currency_per_point'] * 1000)
        guess_about = C.GUESS_ABOUT[player.treatment]
        percent_normal = 100 - C.PERCENT_IDEAL
        return dict(
            attempt_number=player.attempt_number,
            wrong_questions_list=wrong_questions_list,
            participation_fee=participation_fee,
            thousand_points=thousand_points,
            guess_about=guess_about,
            percent_normal=percent_normal,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        required_fields = ComprehensionCheck.get_form_fields(player)
        if exclude_on_incomplete_timeout(
            player,
            timeout_happened,
            required_fields,
            'ComprehensionCheck',
        ):
            return

        # Increment attempt number
        player.attempt_number += 1

        # Check which questions are wrong
        wrong_list = []
        if player.q1 != C.SOLUTIONS['q1']:
            wrong_list.append('q1')
        if player.q2 != C.SOLUTIONS['q2']:
            wrong_list.append('q2')
        if player.q3 != C.SOLUTIONS['q3']:
            wrong_list.append('q3')
        if player.treatment:
            if player.q4t != C.SOLUTIONS['q4t']:
                wrong_list.append('q4t')
            if player.q5t != C.SOLUTIONS['q5t']:
                wrong_list.append('q5t')
        else:
            if player.q4c != C.SOLUTIONS['q4c']:
                wrong_list.append('q4c')
            if player.q5c != C.SOLUTIONS['q5c']:
                wrong_list.append('q5c')

        player.num_wrong = len(wrong_list)
        player.wrong_questions = ','.join(wrong_list)

        # Store wrong questions for each attempt
        if player.attempt_number == 1:
            player.participant.vars['wrong_questions_attempt1'] = player.wrong_questions
        elif player.attempt_number == 2:
            player.participant.vars['wrong_questions_attempt2'] = player.wrong_questions

        # Exclusion / success logic
        if player.num_wrong >= 4:
            player.excluded = True  # immediately exclude
            player.success_attempt = None
        elif player.num_wrong == 0:
            player.success_attempt = player.attempt_number
        else:
            player.success_attempt = 0  # allow second attempt

        player.participant.vars['success_attempt'] = player.field_maybe_none('success_attempt')
        player.participant.vars['attempt_number'] = player.attempt_number
        player.participant.vars['excluded'] = player.excluded

        if player.participant.vars['total_wrong'] is None:
            player.participant.vars['total_wrong'] = 0
        player.participant.vars['total_wrong'] += player.num_wrong


class ShowCorrectAnswers(Page):
    get_timeout_seconds = page_timeout('show_correct_answer')
    @staticmethod
    def is_displayed(player):
        # Show correct answers only if they failed twice but are not excluded
        return player.attempt_number == 2 and player.success_attempt == 0 and not player.excluded

    @staticmethod
    def vars_for_template(player):
        if player.treatment:
            keys = ['q1', 'q2', 'q3', 'q4t', 'q5t']
        else:
            keys = ['q1', 'q2', 'q3', 'q4c', 'q5c']
        solutions = {k: C.SOLUTIONS[k] for k in keys if k in C.SOLUTIONS}
        return dict(solutions=solutions)


class Excluded(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.vars.get('excluded', False)

    @staticmethod
    def vars_for_template(player):
        return dict(
            incomplete_timeout=(
                player.participant.vars.get('exclusion_reason')
                == 'incomplete_timeout'
            )
        )


class Consent(Page):
    get_timeout_seconds = page_timeout('consent')
    form_model = 'player'
    form_fields = ['consent']
    timeout_submission = {'consent': None}

    @staticmethod
    def before_next_page(player, timeout_happened):
        if exclude_on_incomplete_timeout(
            player, timeout_happened, Consent.form_fields, 'Consent'
        ):
            return
        player.participant.vars['consent'] = player.consent


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
    Excluded,
    NoConsent,
]
