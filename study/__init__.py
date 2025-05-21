from otree.api import *
import random, string, json
from instructions_consent import C as base_constants

doc = """
Task
"""


class C(BaseConstants):
    NAME_IN_URL = 'study'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 6  # = number of sessions including trial. Certain pages will only be shown in certain rounds, e.g. predicted and ideal in only rounds 2 and 6
    USE_TIMEOUT = True
    TIMEOUT_SECONDS = 60  # TODO: set this to 600 for the real experiment (10 minutes)
    TIMEOUT_MINUTES = round(TIMEOUT_SECONDS / 60)
    TASK_LENGTH = 4


class Subsession(BaseSubsession):
    dictionary = models.StringField()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # TODO: so far in each round these are newly generated, so save everything in participant variables!!
    performance = models.IntegerField(initial=0, blank=False)
    mistakes = models.IntegerField(initial=0, blank=False)

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
    print('value is', value)
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

    # TODO: select the 5 percent here?


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
    @staticmethod
    def is_displayed(player):
        return player.round_number == 2 or player.round_number == 6

    form_model = 'player'
    form_fields = ['ideal50', 'ideal60', 'ideal70', 'ideal80', 'ideal90', 'ideal100',
                   'ideal110', 'ideal120', 'ideal130', 'ideal140', 'ideal150', 'lastideal']

    @staticmethod
    def vars_for_template(player):
        return {
            'percent_ideal': base_constants.PERCENT_IDEAL,
        }


class Predicted(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 2 or player.round_number == 6

    form_model = 'player'
    form_fields = ['predicted50', 'predicted60', 'predicted70', 'predicted80', 'predicted90',
                   'predicted100', 'predicted110', 'predicted120', 'predicted130', 'predicted140',
                   'predicted150', 'lastpredicted']


class Belief(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number > 1

    form_model = 'player'
    form_fields = ['belief']


class Signal(Page):
    @staticmethod
    def is_displayed(player):
        return 1 < player.round_number < 6


class Work(Page):  # in period 5, we tell the participants the number of tasks they have to do here
    pass  # TODO: only display this to the x percent in period 6 or in all periods but different text?


class Task(Page):
    live_method = live_update_performance
    form_model = 'player'
    form_fields = ['performance', 'mistakes']
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


class Results(Page):
    pass  # this we don't need actually. or do we?


class Survey(Page):
    @staticmethod
    def is_displayed(player):
        return 1 < player.round_number < 6


page_sequence = [
    Interval,
    Ideal,
    Predicted,
    Belief,
    Signal,
    Work,
    Task,
    Results,
    Survey
]
