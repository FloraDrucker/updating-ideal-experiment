from otree.api import *
import random, string, json
from instructions_consent import C as base_constants

doc = """
Study
"""


class C(BaseConstants):
    NAME_IN_URL = 'study'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 6  # = number of sessions including trial. Certain pages will only be shown in certain rounds, e.g. predicted and ideal in only rounds 2 and 6
    PARTS = {
        1: 'the Trial Part',
        2: 'Part One',
        3: 'Part Two',
        4: 'Part Three',
        5: 'Part Four',
        6: 'Part Five',
    }
    USE_TIMEOUT = True
    TIMEOUT_SECONDS = 20  # TODO: set this to 600 for the real experiment (10 minutes)
    TIMEOUT_MINUTES = round(TIMEOUT_SECONDS / 60)
    TASK_LENGTH = 4
    SIGNAL_TIMEOUT = 5  # seconds signal is shown


class Subsession(BaseSubsession):
    dictionary = models.StringField()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    performance = models.IntegerField(initial=0, blank=False)
    mistakes = models.IntegerField(initial=0, blank=False)
    link_click_count = models.IntegerField(initial=0) # Added this to track the links clicked in the Task.html
    active_tab_seconds = models.IntegerField(initial=0) # Added this to track the time spend on the Tab
    # Ideal values
    ideal50 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 50 cents per task?"
    )
    ideal60 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 60 cents per task?"
    )
    ideal70 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 70 cents per task?"
    )
    ideal80 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 80 cents per task?"
    )
    ideal90 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 90 cents per task?"
    )
    ideal100 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 100 cents per task?"
    )
    ideal110 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 110 cents per task?"
    )
    ideal120 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 120 cents per task?"
    )
    ideal130 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 130 cents per task?"
    )
    ideal140 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 140 cents per task?"
    )
    ideal150 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 150 cents per task?"
    )
    lastideal = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do in this round for what you think the task payoff is?"
    )

    # Predicted values
    predicted50 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 50 cents per task?"
    )
    predicted60 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 60 cents per task?"
    )
    predicted70 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 70 cents per task?"
    )
    predicted80 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 80 cents per task?"
    )
    predicted90 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 90 cents per task?"
    )
    predicted100 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 100 cents per task?"
    )
    predicted110 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 110 cents per task?"
    )
    predicted120 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 120 cents per task?"
    )
    predicted130 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 130 cents per task?"
    )
    predicted140 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 140 cents per task?"
    )
    predicted150 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 150 cents per task?"
    )
    lastpredicted = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do in this round for what you think the task payoff is?"
    )

    belief = models.IntegerField(
        blank=False,
        label="What do you think is the true task payoff in cents?"
    )


def belief_error_message(player, value):
    if not base_constants.BENEFIT_RANGE_MIN <= value <= base_constants.BENEFIT_RANGE_MAX:
        return f"Please enter a number between {base_constants.BENEFIT_RANGE_MIN} and {base_constants.BENEFIT_RANGE_MAX}."


def creating_session(subsession: Subsession):
    # Create dictionary
    letters = list(string.ascii_uppercase)
    random.shuffle(letters)
    numbers = []
    N = list(range(100, 1000))
    for i in range(27):
        choice = random.choice(N)
        N.remove(choice)
        numbers.append(choice)
    d = [letters, numbers]
    dictionary = dict([(d[0][i], d[1][i]) for i in range(26)])
    subsession.dictionary = json.dumps(dictionary)

    # define participant variables
    for p in subsession.get_players():
        p.participant.vars['actual'] = {i: None for i in range(C.NUM_ROUNDS)}
        p.participant.vars['belief'] = {i+1: None for i in range(C.NUM_ROUNDS-1)}
        p.participant.vars['ideal'] = {i+1: None for i in range(12)}
        p.participant.vars['predicted'] = {i+1: None for i in range(12)}
        p.participant.vars['link_click_count'] = {i: None for i in range(C.NUM_ROUNDS)}
        p.participant.vars['active_tab_seconds'] = {i: None for i in range(C.NUM_ROUNDS)}
        p.participant.vars['risk_choices'] = {i+1: None for i in range(21)}
        print("Participant:", p.participant.code, "Variables:", p.participant.vars)

    # TODO: select the 3 percent here?


def live_update_performance(player: Player, data):
    own_id = player.id_in_group
    if 'performance' in data:
        perf = data['performance']
        player.performance = perf
        shuffle = True
        print('received ', perf, 'shuffle?', shuffle)
    else:
        shuffle = True
        print('received nothing, shuffle?', shuffle)
    answer = dict(performance=player.performance, shuffle=shuffle)
    return {own_id: answer}


# PAGES
class PartStart(Page):
    @staticmethod
    def vars_for_template(player):
        return {
            'part': C.PARTS[player.round_number]
        }


class Interval(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 2  # only shown in the first real round

    @staticmethod
    def vars_for_template(player):
        return {
            'benefit_min': base_constants.BENEFIT_RANGE_MIN,
            'benefit_max': base_constants.BENEFIT_RANGE_MAX,
        }


class Ideal(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        if player.round_number == 2:
            return ['ideal50', 'ideal60', 'ideal70', 'ideal80', 'ideal90', 'ideal100',
                    'ideal110', 'ideal120', 'ideal130', 'ideal140', 'ideal150']
        elif player.round_number == 6:
            return ['lastideal']
        else:
            return []

    @staticmethod
    def is_displayed(player):
        return player.round_number == 2 or player.round_number == 6

    @staticmethod
    def vars_for_template(player):
        return {
            'percent_ideal': base_constants.PERCENT_IDEAL,
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number == 2:
            player.participant.vars['ideal'][1] = player.ideal50
            player.participant.vars['ideal'][2] = player.ideal60
            player.participant.vars['ideal'][3] = player.ideal70
            player.participant.vars['ideal'][4] = player.ideal80
            player.participant.vars['ideal'][5] = player.ideal90
            player.participant.vars['ideal'][6] = player.ideal100
            player.participant.vars['ideal'][7] = player.ideal110
            player.participant.vars['ideal'][8] = player.ideal120
            player.participant.vars['ideal'][9] = player.ideal130
            player.participant.vars['ideal'][10] = player.ideal140
            player.participant.vars['ideal'][11] = player.ideal150
        elif player.round_number == 6:
            player.participant.vars['ideal'][12] = player.lastideal
        else:
            pass

        print("Participant:", player.participant.code, "Variables:", player.participant.vars)


class Predicted(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        if player.round_number == 2:
            return ['predicted50', 'predicted60', 'predicted70', 'predicted80', 'predicted90',
                   'predicted100', 'predicted110', 'predicted120', 'predicted130', 'predicted140',
                   'predicted150']
        elif player.round_number == 6:
            return ['lastpredicted']
        else:
            return []

    @staticmethod
    def is_displayed(player):
        return player.round_number == 2 or player.round_number == 6

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number == 2:
            player.participant.vars['predicted'][1] = player.predicted50
            player.participant.vars['predicted'][2] = player.predicted60
            player.participant.vars['predicted'][3] = player.predicted70
            player.participant.vars['predicted'][4] = player.predicted80
            player.participant.vars['predicted'][5] = player.predicted90
            player.participant.vars['predicted'][6] = player.predicted100
            player.participant.vars['predicted'][7] = player.predicted110
            player.participant.vars['predicted'][8] = player.predicted120
            player.participant.vars['predicted'][9] = player.predicted130
            player.participant.vars['predicted'][10] = player.predicted140
            player.participant.vars['predicted'][11] = player.predicted150
        elif player.round_number == 6:
            player.participant.vars['predicted'][12] = player.lastpredicted
        else:
            pass

        print("Participant:", player.participant.code, "Variables:", player.participant.vars)


class Performance(Page):  # display performance from the previous round

    @staticmethod
    def is_displayed(player):
        return player.round_number > 2

    @staticmethod
    def vars_for_template(player):
        return {
            'performance': player.participant.vars['actual'][player.round_number-2]
        }


class Belief(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number > 1

    form_model = 'player'
    form_fields = ['belief']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number > 1:
            player.participant.vars['belief'][player.round_number-1] = player.belief
        print("Participant:", player.participant.code, "Variables:", player.participant.vars)  # TODO: remind them here about the interval again?


class Signal(Page):
    timeout_seconds = C.SIGNAL_TIMEOUT

    @staticmethod
    def is_displayed(player):
        return 1 < player.round_number < 6


class Work(Page):  # in period 5, we tell the participants the number of tasks they have to do here
    pass  # TODO: only display this to the x percent in period 6 or in all periods but different text?


class Task(Page):
    live_method = live_update_performance
    form_model = 'player'
    form_fields = ['performance', 'mistakes', 'link_click_count', 'active_tab_seconds',]  # TODO: save mistakes!
    if C.USE_TIMEOUT:
        timeout_seconds = C.TIMEOUT_SECONDS

    @staticmethod
    def vars_for_template(player):
        letters_per_word = C.TASK_LENGTH
        task_list = [j for j in range(letters_per_word)]
        legend_list = [j for j in range(26)]
        return {
            'legend_list': legend_list,
            'letters_per_word': letters_per_word,
            'task_list': task_list,
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vars['actual'][player.round_number-1] = player.performance
        player.participant.vars['link_click_count'][player.round_number-1] = player.link_click_count
        player.participant.vars['active_tab_seconds'][player.round_number-1] = player.active_tab_seconds
        print("Participant:", player.participant.code, "Variables:", player.participant.vars)


class Results(Page):
    pass  # this we don't need actually. or do we?


class Survey1(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 2


class Survey2(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 3


class Survey3(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 4


class Survey4(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 5


class Survey5(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 6


class FinalPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        config = player.session.config
        return {
            'completion_url': config.get('prolific_completion_url', ''),
            'completion_code': config.get('prolific_completion_code', ''),
        }


page_sequence = [
    PartStart,
    Interval,
    Ideal,
    Predicted,
    Performance,
    Belief,
    Signal,
    Work,
    Task,
    Results,
    Survey1,
    Survey2,
    Survey3,
    Survey4,
    Survey5,
    FinalPage
]
