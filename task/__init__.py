from otree.api import *
import random, string, json

doc = """
Task
"""


class C(BaseConstants):
    NAME_IN_URL = 'task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    USE_TIMEOUT = True
    TIMEOUT_SECONDS = 120
    TASK_LENGTH = 4


class Subsession(BaseSubsession):
    dictionary = models.StringField()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    performance = models.IntegerField(initial=0, blank=False)
    mistakes = models.IntegerField(initial=0, blank=False)


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


def live_update_performance(player: Player, data):
    own_id = player.id_in_group
    if 'performance' in data:
        perf = data['performance']
        player.performance = perf
        shuffle = False
        print('received ', perf, 'shuffle?', shuffle)
    else:
        shuffle = True
        print('received nothing, shuffle?', shuffle)
    answer = dict(performance=player.performance, shuffle=shuffle)
    return {own_id: answer}


# PAGES
class Task(Page):
    live_method = live_update_performance
    form_model = 'player'
    form_fields = ['performance', 'mistakes']
    if C.USE_TIMEOUT:
        timeout_seconds = C.TIMEOUT_SECONDS

    @staticmethod
    def vars_for_template(player: Player):
        letters_per_word = C.TASK_LENGTH
        task_list = [j for j in range(letters_per_word)]
        legend_list = [j for j in range(26)]
        return {
            'legend_list': legend_list,
            'letters_per_word': letters_per_word,
            'task_list': task_list,
        }


class Results(Page):
        pass


page_sequence = [Task, Results]
