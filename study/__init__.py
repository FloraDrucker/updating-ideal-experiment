from otree.api import *
import random, string, json
from instructions_consent import C as base_constants
import numpy as np

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
    TIMEOUT_SECONDS = 30  # TODO: set this to 600 for the real experiment (10 minutes)
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
    do_ideal = models.BooleanField(initial=False) # whether the participant has to do the stated ideal number of tasks
    ideal_to_do = models.IntegerField(default=999)
    ideal_index = models.IntegerField(null=True, blank=True, default=None)

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

    risk_0 = models.IntegerField(
        choices=[
            [0, '0 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_50 = models.IntegerField(
        choices=[
            [0, '50 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_100 = models.IntegerField(
        choices=[
            [0, '100 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_150 = models.IntegerField(
        choices=[
            [0, '150 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_200 = models.IntegerField(
        choices=[
            [0, '200 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_250 = models.IntegerField(
        choices=[
            [0, '250 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_300 = models.IntegerField(
        choices=[
            [0, '300 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_350 = models.IntegerField(
        choices=[
            [0, '350 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_400 = models.IntegerField(
        choices=[
            [0, '400 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_450 = models.IntegerField(
        choices=[
            [0, '450 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_500 = models.IntegerField(
        choices=[
            [0, '500 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_550 = models.IntegerField(
        choices=[
            [0, '550 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_600 = models.IntegerField(
        choices=[
            [0, '600 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_650 = models.IntegerField(
        choices=[
            [0, '650 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_700 = models.IntegerField(
        choices=[
            [0, '700 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_750 = models.IntegerField(
        choices=[
            [0, '750 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_800 = models.IntegerField(
        choices=[
            [0, '800 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_850 = models.IntegerField(
        choices=[
            [0, '850 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_900 = models.IntegerField(
        choices=[
            [0, '900 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_950 = models.IntegerField(
        choices=[
            [0, '950 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    risk_1000 = models.IntegerField(
        choices=[
            [0, '1000 points'],
            [1, '50 % chance of 1000 points, 50 % chance of 0 points'],
        ],
        widget=widgets.RadioSelectHorizontal,
    )

    gender = models.IntegerField(
        choices=[
            [0, 'Male'],
            [1, 'Female'],
            [2, 'Diverse'],
        ],
        blank=False,
        label='What is your gender?'
    )

    age = models.IntegerField(
        choices=[(i, str(i)) for i in range(18, 101)],
        blank=False,
        label='What is your age?'
    )

    employment = models.IntegerField(
        choices=[
            [0, 'Unemployed and not currently looking for work'],
            [1, 'Unemployed and looking for work'],
            [2, 'Part-time employee'],
            [3, 'Full-time employee'],
            [4, 'Self-employed or business owner'],
            [5, 'Retired'],
            [6, 'Student'],
        ],
        blank=False,
        label='What is your employment status?'
    )

    education = models.IntegerField(
        choices=[
            [0, 'Less than high school (no diploma)'],
            [1, 'High school graduate (includes GED)'],
            [2, 'Some college, no degree'],
            [3, 'Associate degree (e.g., AA, AS)'],
            [4, 'Bachelor’s degree (e.g., BA, BS)'],
            [5, 'Master’s degree (e.g., MA, MS, MBA)'],
            [6, 'Professional degree (e.g., MD, JD)'],
            [7, 'Doctorate degree (e.g., PhD, EdD)'],
        ],
        blank=False,
        label='What is your highest level of education?'
    )

    socialclass = models.IntegerField(
        choices=[
            [0, 'Lower class or poor'],
            [1, 'Working class'],
            [2, 'Middle class'],
            [3, 'Upper-middle class'],
            [4, 'Upper class'],
        ],
        blank=False,
        label='If you had to use one of these five commonly-used names to describe your social class, wich one would it be?'
    )

    children = models.IntegerField(
        min=0,
        blank=False,
        label='How many children do you have?'
    )

    mathgrade = models.StringField(
        choices=[
            'A', 'A-',
            'B+', 'B', 'B-',
            'C+', 'C', 'C-',
            'D+', 'D', 'D-',
            'F'
        ],
        blank=False,
        label='What was your last math grade?'
    )

    BSCS_temptation = models.IntegerField(
        label="I am good at resisting temptation.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    BSCS_badhabits = models.IntegerField(
        label="I have a hard time breaking bad habits.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    BSCS_lazy = models.IntegerField(
        label="I am lazy.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )


    BSCS_inappropriate = models.IntegerField(
        label="I say inappropriate things.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )


    BSCS_dobadthings = models.IntegerField(
        label="I do certain things that are bad for me, if they are fun.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )


    BSCS_refusebad = models.IntegerField(
        label="I refuse things that are bad for me.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    BSCS_morediscipline = models.IntegerField(
        label="I wish I had more self-discipline.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    BSCS_irondiscipline = models.IntegerField(
        label="People would say that I have iron self-discipline.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )


    BSCS_pleasure = models.IntegerField(
        label="Pleasure and fun sometimes keep me from getting work done.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )


    BSCS_concentrating = models.IntegerField(
        label="I have trouble concentrating.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    BSCS_work = models.IntegerField(
        label="I am able to work effectively toward long-term goals.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    BSCS_stop = models.IntegerField(
        label="Sometimes I can't stop myself from doing something, even if I know it is wrong.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    BSCS_alternatives = models.IntegerField(
        label="I often act without thinking through all the alternatives.",
        choices=[
            [1, '1 - Not at all like me'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5 - Very much like me'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    averagetask = models.FloatField(
        min=0,
        max=555,
        blank=False,
        label='What is the average of the following five numbers? 123, 88, 147, 102, 95'
    )

    ballsremembered1 = models.IntegerField(
        choices=[
            [0, '0'],
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7'],
            [8, '8'],
            [9, '9'],
            [10, '10'],
            [11, 'I cannot remember how many times I have seen a ball with this number on it.'],
        ],
        blank=False,
        label='How many times have you seen a ball with the number 137 on it over the course of the experiment?'
    )

    ballsremembered2 = models.IntegerField(
        choices=[
            [0, '0'],
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7'],
            [8, '8'],
            [9, '9'],
            [10, '10'],
            [11, 'I cannot remember how many times I have seen a ball with this number on it.'],
        ],
        blank=False,
        label='How many times have you seen a ball with the number 109 on it over the course of the experiment?'
    )

    ballsremembered3 = models.IntegerField(
        choices=[
            [0, '0'],
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7'],
            [8, '8'],
            [9, '9'],
            [10, '10'],
            [11, 'I cannot remember how many times I have seen a ball with this number on it.'],
        ],
        blank=False,
        label='How many times have you seen a ball with the number 122 on it over the course of the experiment?'
    )

    screenshot = models.BooleanField(
        choices=[[True, 'Yes'], [False, 'No']],
        widget=widgets.RadioSelect,
        blank=False,
        label='Did you make a screenshot/photo of the balls shown to you or wrote the numbers on them down?'
    )

    GPS_patience = models.IntegerField(
        label="How willing are you to give up something that is beneficial for you today in order to benefit more from that in the future on a scale from 0 'Completely unwilling to do so' to 10 'Very willing to do so'?",
        choices=[
            [0, '0'],
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7'],
            [8, '8'],
            [9, '9'],
            [10, '10'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    GPS_altruism1 = models.IntegerField(
        label="How willing are you to give to good causes without expecting anything in return on a scale from 0 'Completely unwilling to do so' to 10 'Very willing to do so'?",
        choices=[
            [0, '0'],
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7'],
            [8, '8'],
            [9, '9'],
            [10, '10'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    GPS_altruism2 = models.IntegerField(
        min=0,
        max=1600,
        blank=False,
        label='Imagine the following situation: Today you unexpectedly received 1,600 U.S. dollars. How much of this amount would you donate to a good cause? (Values between 0 and 1,600 are allowed)'
    )

    GPS_postpone = models.IntegerField(
        label="Do you tend to postpone tasks even if you know it would be better to do them right away on a scale from 0 'Completely unwilling to do so' to 10 'Very willing to do so'?",
        choices=[
            [0, '0'],
            [1, '1'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7'],
            [8, '8'],
            [9, '9'],
            [10, '10'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_openness1 = models.IntegerField(
        label = "I see myself as someone who is original, comes up with new ideas.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_openness2 = models.IntegerField(
        label = "I see myself as someone who values artistic, aesthetic experiences.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_openness3 = models.IntegerField(
        label="I see myself as someone who has an active imagination.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_openness4 = models.IntegerField(
        label="I see myself as someone who is eager for knowledge.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_conscientious1 = models.IntegerField(
        label="I see myself as someone who does a thorough job.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_conscientious2 = models.IntegerField(
        label="I see myself as someone who tends to be lazy.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_conscientious3 = models.IntegerField(
        label="I see myself as someone who does things effectively and efficiently.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_extraversion1 = models.IntegerField(
        label="I see myself as someone who is communicative, talkative.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_extraversion2 = models.IntegerField(
        label="I see myself as someone who is outgoing, sociable.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_extraversion3 = models.IntegerField(
        label="I see myself as someone who is reserved.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_agreeable1 = models.IntegerField(
        label="I see myself as someone who is sometimes somewhat rude to others.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_agreeable2 = models.IntegerField(
        label="I see myself as someone who has a forgiving nature.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_agreeable3 = models.IntegerField(
        label="I see myself as someone who is considerate and kind to others.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_neuroticism1 = models.IntegerField(
        label="I see myself as someone who worries a lot.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_neuroticism2 = models.IntegerField(
        label="I see myself as someone who gets nervous easily.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    big5_neuroticism3 = models.IntegerField(
        label="I see myself as someone who is relaxed, handles stress well.",
        choices=[
            [1, '1 - Not at all'],
            [2, '2'],
            [3, '3'],
            [4, '4'],
            [5, '5'],
            [6, '6'],
            [7, '7 - Absolutely'],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    #Wechsler Level
    digitspan_max_level = models.IntegerField(
        initial=0,
        min=0,
        max=8,
        label="Max digit-span level reached"
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
        p.participant.vars['do_ideal'] = False
        p.participant.vars['ideal_to_do'] = None
        p.participant.vars['ideal_index'] = None
        p.participant.vars['link_click_count'] = {i: None for i in range(C.NUM_ROUNDS)}
        p.participant.vars['active_tab_seconds'] = {i: None for i in range(C.NUM_ROUNDS)}
        p.participant.vars['risk_choices'] = {i+1: None for i in range(21)}
        print("Participant:", p.participant.code, "Variables:", p.participant.vars)


# This is the Live Send code, so that performance etc can be stored immediately
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
    if 'link_click_count' in data:
        player.link_click_count = data['link_click_count']
        shuffle = False
    if 'active_tab_seconds' in data:
        player.active_tab_seconds = data[('active_tab_seconds')]
        shuffle = False
    if 'mistakes' in data:
        player.mistakes = data['mistakes']
        shuffle = False
    answer = dict(performance=player.performance, link_click_count=player.link_click_count, active_tab_seconds=player.active_tab_seconds, mistakes=player.mistakes, shuffle=shuffle)
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
        print("Participant:", player.participant.code, "Variables:", player.participant.vars)
        # TODO: remind them here about the interval again?

        if player.round_number == 6:
            prob_ideal = round(base_constants.PERCENT_IDEAL/100, 2)
            player.do_ideal = bool(np.random.choice([True, False],
                                               p=[prob_ideal, 1-prob_ideal]))
            player.participant.vars['do_ideal'] = player.do_ideal

        # do either the ideal stated in the first round or in the last round:
            if player.do_ideal:
                player.ideal_index = int(np.random.choice([8, 12]))
                player.ideal_to_do = player.participant.vars['ideal'][player.ideal_index]
                player.participant.vars['ideal_to_do'] = player.ideal_to_do
                player.participant.vars['ideal_index'] = player.ideal_index
                print("Ideal to do:", player.ideal_to_do)
        print("Participant:", player.participant.code, "Variables:", player.participant.vars)


class Signal(Page):
    timeout_seconds = C.SIGNAL_TIMEOUT

    @staticmethod
    def is_displayed(player):
        return 1 < player.round_number < 6


class Work(Page):  # in period 5, we tell the participants the number of tasks they have to do here
    @staticmethod
    def is_displayed(player):
        return player.round_number > 1

    @staticmethod
    def vars_for_template(player):
        if player.do_ideal:
            part_ideal_elicited = {8: 'first part', 12: 'last part'}
            return {
                'ideal_to_do': player.ideal_to_do,
                'percent_ideal': base_constants.PERCENT_IDEAL,
                'part_ideal_elicited': part_ideal_elicited[player.ideal_index]
            }
        else:
            pass


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
            'letters_per_word': letters_per_word,
            'legend_list': legend_list,
            'task_list': task_list,
            'required_tasks': player.ideal_to_do,
        }

    @staticmethod
    def js_vars(player):
        return dict(
            required_tasks=player.ideal_to_do,
            timeout_seconds=C.TIMEOUT_SECONDS,
        )

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

    form_model = 'player'
    form_fields = [
        'gender', 'age', 'employment', 'education', 'socialclass', 'children', 'mathgrade',
        'big5_openness1', 'big5_openness2', 'big5_openness3', 'big5_openness4'
    ]


class Survey2(Page):
    form_model = 'player'
    form_fields = ['digitspan_max_level']
    @staticmethod
    def is_displayed(player):
        return player.round_number == 3


class Survey3(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 4

    form_model = 'player'
    form_fields = [
        'risk_0', 'risk_50', 'risk_100', 'risk_150', 'risk_200',
        'risk_250', 'risk_300', 'risk_350', 'risk_400', 'risk_450',
        'risk_500', 'risk_550', 'risk_600', 'risk_650', 'risk_700',
        'risk_750', 'risk_800', 'risk_850', 'risk_900', 'risk_950',
        'risk_1000',
        'big5_conscientious1', 'big5_conscientious2', 'big5_conscientious3',
        'big5_extraversion1', 'big5_extraversion2', 'big5_extraversion3'
    ]

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vars['risk_choices'][1] = player.risk_0
        player.participant.vars['risk_choices'][2] = player.risk_50
        player.participant.vars['risk_choices'][3] = player.risk_100
        player.participant.vars['risk_choices'][4] = player.risk_150
        player.participant.vars['risk_choices'][5] = player.risk_200
        player.participant.vars['risk_choices'][6] = player.risk_250
        player.participant.vars['risk_choices'][7] = player.risk_300
        player.participant.vars['risk_choices'][8] = player.risk_350
        player.participant.vars['risk_choices'][9] = player.risk_400
        player.participant.vars['risk_choices'][10] = player.risk_450
        player.participant.vars['risk_choices'][11] = player.risk_500
        player.participant.vars['risk_choices'][12] = player.risk_550
        player.participant.vars['risk_choices'][13] = player.risk_600
        player.participant.vars['risk_choices'][14] = player.risk_650
        player.participant.vars['risk_choices'][15] = player.risk_700
        player.participant.vars['risk_choices'][16] = player.risk_750
        player.participant.vars['risk_choices'][17] = player.risk_800
        player.participant.vars['risk_choices'][18] = player.risk_850
        player.participant.vars['risk_choices'][19] = player.risk_900
        player.participant.vars['risk_choices'][20] = player.risk_950
        player.participant.vars['risk_choices'][21] = player.risk_1000
        print("Participant:", player.participant.code, "Variables:", player.participant.vars)


class Survey4(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 5

    form_model = 'player'
    form_fields = [
        'GPS_patience', 'GPS_altruism1', 'GPS_altruism2', 'GPS_postpone',
        'big5_agreeable1', 'big5_agreeable2', 'big5_agreeable3',
        'big5_neuroticism1', 'big5_neuroticism2', 'big5_neuroticism3'
    ]


class Survey5(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 6

    form_model = 'player'
    form_fields = [
        'BSCS_temptation', 'BSCS_badhabits', 'BSCS_lazy', 'BSCS_inappropriate',
        'BSCS_dobadthings', 'BSCS_refusebad', 'BSCS_morediscipline', 'BSCS_irondiscipline',
        'BSCS_pleasure', 'BSCS_concentrating', 'BSCS_work', 'BSCS_stop',
        'BSCS_alternatives', 'averagetask', 'ballsremembered1', 'ballsremembered2',
        'ballsremembered3','screenshot'
    ]


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
