from otree.api import *
import random, string, json
from instructions_consent import C as base_constants
import numpy as np
import time

doc = """
Study
"""


class C(BaseConstants):
    NAME_IN_URL = 'study'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 6  # = number of sessions including trial. Certain pages will only be shown in certain rounds, e.g. predicted and ideal in only rounds 2 and 6
    PARTS = {
        0: 'the trial part',
        1: 'part one',
        2: 'part two',
        3: 'part three',
        4: 'part four',
        5: 'part five',
    }
    USE_TIMEOUT = True
    # TIMEOUT_SECONDS = 600
    # TIMEOUT_MINUTES = round(TIMEOUT_SECONDS / 60)
    TASK_LENGTH = 4
    SIGNAL_TIMEOUT = 5  # seconds signal is shown
    RISK_LARGE = 1000
    RISK_STEP = 50
    RISK_FIXED = {}
    for i in range(round(RISK_LARGE/50)+1):
        j = i*RISK_STEP
        RISK_FIXED[i] = j
    RISK_CHOICES = {}
    RISK_OPTIONS = {}
    for i in RISK_FIXED.keys():
        j = RISK_FIXED[i]
        RISK_CHOICES[i] = f"{j} points or 50 % chance of 1000 points, 50 % chance of 0 points"
        RISK_OPTIONS[i] = {0: f"{j} points", 1: "50 % chance of 1000 points, 50 % chance of 0 points"}
    PERCENT_IDEAL_PART5 = 2

class Subsession(BaseSubsession):
    dictionary = models.StringField()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    task_start_time = models.FloatField(initial=0)
    current_dict = models.LongStringField()
    current_word = models.LongStringField()
    performance = models.IntegerField(initial=0, blank=False)
    mistakes = models.IntegerField(initial=0, blank=False)
    work_seconds = models.IntegerField(initial=0) # This tracks the working time
    nonwork_seconds = models.IntegerField(initial=0)  # Tracking non-work time
    stopped_work = models.BooleanField(initial=False)
    attention_checks_received = models.IntegerField(initial=0)
    attention_checks_failed = models.IntegerField(initial=0)
    do_ideal = models.BooleanField(initial=False) # whether the participant has to do the stated ideal number of tasks
    ideal_to_do = models.IntegerField(default=999)
    ideal_index = models.IntegerField(null=True, blank=True, default=None)
    task_chosen_part = models.IntegerField(blank=False)
    prob = models.FloatField(blank=False)
    belief_chosen_part = models.IntegerField(blank=False)
    payment_for_belief = models.IntegerField(blank=False)
    risk_chosen = models.IntegerField(blank=False)
    risk_payment = models.IntegerField(blank=False)
    choice_in_risk_chosen = models.IntegerField(blank=False)
    comments = models.LongStringField(blank=True)

    signal_start_time = models.FloatField(initial=0)

    # Ideal values
    ideal50 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 50 points per task?"
    )
    ideal60 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 60 points per task?"
    )
    ideal70 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 70 points per task?"
    )
    ideal80 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 80 points per task?"
    )
    ideal90 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 90 points per task?"
    )
    ideal100 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 100 points per task?"
    )
    ideal110 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 110 points per task?"
    )
    ideal120 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 120 points per task?"
    )
    ideal130 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 130 points per task?"
    )
    ideal140 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 140 points per task?"
    )
    ideal150 = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do for 150 points per task?"
    )
    lastideal_t = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do in this round for what you think the task payoff is?"
    )

    lastideal_c = models.IntegerField(
        blank=False,
        label="How many tasks do you ideally want to do in this round?"
    )

    # Predicted values
    predicted50 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 50 points per task?"
    )
    predicted60 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 60 points per task?"
    )
    predicted70 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 70 points per task?"
    )
    predicted80 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 80 points per task?"
    )
    predicted90 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 90 points per task?"
    )
    predicted100 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 100 points per task?"
    )
    predicted110 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 110 points per task?"
    )
    predicted120 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 120 points per task?"
    )
    predicted130 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 130 points per task?"
    )
    predicted140 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 140 points per task?"
    )
    predicted150 = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do for 150 points per task?"
    )
    lastpredicted_t = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do in this round for what you think the task payoff is?"
    )

    lastpredicted_c = models.IntegerField(
        blank=False,
        label="How many tasks do you predict you will do in this round?"
    )

    belief_t = models.IntegerField(
        blank=False,
        label="What do you think is the task payoff in points?"
    )

    belief_c = models.IntegerField(
        blank=False,
        label="What do you think is the chosen number?"
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
        label='If you had to use one of these five commonly-used names to describe your social class, which one would it be?'
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
        label='What is the average of the following five numbers? 123, 88, 147, 102, 95. Please do not use a calculator.'
    )

    ballsremembered1 = models.IntegerField(
        choices=[
            [-1, 'I cannot remember how many times I have seen a ball with this number on it.'],
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
        blank=False,
        label='How many times have you seen a ball with the number 128 on it over the course of the experiment?'
    )

    ballsremembered2 = models.IntegerField(
        choices=[
            [-1, 'I cannot remember how many times I have seen a ball with this number on it.'],
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
        blank=False,
        label='How many times have you seen a ball with the number 102 on it over the course of the experiment?'
    )

    ballsremembered3 = models.IntegerField(
        choices=[
            [-1, 'I cannot remember how many times I have seen a ball with this number on it.'],
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
        blank=False,
        label='How many times have you seen a ball with the number 136 on it over the course of the experiment?'
    )

    screenshot = models.BooleanField(
        choices=[[True, 'Yes'], [False, 'No']],
        widget=widgets.RadioSelect,
        blank=False,
        label='Did you make a screenshot/photo of the balls shown to you or write the numbers on them down?'
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

    GPS_timediscounting = models.IntegerField(
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

    ai_integral = models.IntegerField(
        choices=[
            [1, '1'],
            [2, '√π ≈ 1.772'],
            [3, 'π ≈ 3.142'],
            [4, "I don’t know the answer"],
        ],
        widget=widgets.RadioSelectHorizontal,
        blank=False
    )

    #Wechsler Level
    digitspan_max_level = models.IntegerField(
        initial=0,
        min=0,
        max=9,
        label="Max digit-span level reached"
    )


def belief_t_error_message(player, value):
    if not base_constants.BENEFIT_RANGE_MIN <= value <= base_constants.BENEFIT_RANGE_MAX:
        return f"Please enter a number between {base_constants.BENEFIT_RANGE_MIN} and {base_constants.BENEFIT_RANGE_MAX}."


def belief_c_error_message(player, value):
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
        ppvars = p.participant.vars

        # Task
        ppvars['actual'] = {i: None for i in range(C.NUM_ROUNDS)}
        ppvars['mistakes'] = {i: None for i in range(C.NUM_ROUNDS)}
        ppvars['belief'] = {i+1: None for i in range(C.NUM_ROUNDS-1)}
        ppvars['ideal'] = {i+1: None for i in range(12)}
        ppvars['predicted'] = {i+1: None for i in range(12)}
        ppvars['do_ideal'] = False
        ppvars['ideal_to_do'] = None
        ppvars['ideal_index'] = None
        ppvars['work_seconds'] = {i: None for i in range(C.NUM_ROUNDS)}
        ppvars['nonwork_seconds'] = {i: None for i in range(C.NUM_ROUNDS)}
        ppvars['attention_checks_received'] = {i: 0 for i in range(C.NUM_ROUNDS)}
        ppvars['attention_checks_failed'] = {i: 0 for i in range(C.NUM_ROUNDS)}

        # Risk preferences
        ppvars['risk_choices'] = {i: None for i in range(21)}

        # Demographics
        ppvars['gender'] = None
        ppvars['age'] = None
        ppvars['employment'] = None
        ppvars['education'] = None
        ppvars['socialclass'] = None
        ppvars['children'] = None
        ppvars['mathgrade'] = None

        # BSCS
        ppvars['BSCS_temptation'] = None
        ppvars['BSCS_badhabits'] = None
        ppvars['BSCS_lazy'] = None
        ppvars['BSCS_inappropriate'] = None
        ppvars['BSCS_dobadthings'] = None
        ppvars['BSCS_refusebad'] = None
        ppvars['BSCS_morediscipline'] = None
        ppvars['BSCS_irondiscipline'] = None
        ppvars['BSCS_pleasure'] = None
        ppvars['BSCS_concentrating'] = None
        ppvars['BSCS_work'] = None
        ppvars['BSCS_stop'] = None
        ppvars['BSCS_alternatives'] = None

        # Memory and averaging skills
        ppvars['averagetask'] = None
        ppvars['ballsremembered1'] = None
        ppvars['ballsremembered2'] = None
        ppvars['ballsremembered3'] = None
        ppvars['screenshot'] = None
        ppvars['ai_integral'] = None

        # Wechsler
        ppvars['digitspan_max_level'] = None

        # GPS
        ppvars['GPS_patience'] = None
        ppvars['GPS_altruism1'] = None
        ppvars['GPS_altruism2'] = None
        ppvars['GPS_timediscounting'] = None

        # Big five
        ppvars['big5_openness1'] = None
        ppvars['big5_openness2'] = None
        ppvars['big5_openness3'] = None
        ppvars['big5_openness4'] = None
        ppvars['big5_conscientious1'] = None
        ppvars['big5_conscientious2'] = None
        ppvars['big5_conscientious3'] = None
        ppvars['big5_extraversion1'] = None
        ppvars['big5_extraversion2'] = None
        ppvars['big5_extraversion3'] = None
        ppvars['big5_agreeable1'] = None
        ppvars['big5_agreeable2'] = None
        ppvars['big5_agreeable3'] = None
        ppvars['big5_neuroticism1'] = None
        ppvars['big5_neuroticism2'] = None
        ppvars['big5_neuroticism3'] = None

        # Variables for payment
        ppvars['task_chosen_part'] = None
        ppvars['prob'] = None
        ppvars['belief_chosen_part'] = None
        ppvars['payment_for_belief'] = None
        ppvars['risk_chosen'] = None
        ppvars['risk_payment'] = None
        ppvars['choice_in_risk_chosen'] = None
        ppvars['total_payment'] = None
        ppvars['comments'] = None


def build_random_dict():
    import string, random
    letters = list(string.ascii_uppercase)
    numbers = random.sample(range(100, 1000), 26)
    random.shuffle(letters)
    return dict(zip(letters, numbers))

def build_random_word(k=4):
    import string, random
    return random.sample(list(string.ascii_uppercase), k)

# This is the Live Send code, so that performance etc can be stored immediately
def live_update_performance(player: Player, data):

    pid = player.id_in_group

    # ------------------------------------------------------------
    # INIT (first time the page loads)
    # ------------------------------------------------------------
    if data.get('init'):
        if not player.field_maybe_none('current_dict') or not player.field_maybe_none('current_word'):
            d = build_random_dict()
            w = build_random_word(C.TASK_LENGTH)
            player.current_dict = json.dumps(d)
            player.current_word = json.dumps(w)
        else:
            d = json.loads(player.current_dict)
            w = json.loads(player.current_word)

        return {
            pid: dict(
                init=True,
                performance=player.performance,
                mistakes=player.mistakes,
                work_seconds=player.work_seconds,
                dict=d,
                word=w,
                shuffle=False
            )
        }

    # ------------------------------------------------------------
    # REQUEST_UPDATE (tab refocus, but no state changes)
    # ------------------------------------------------------------
    if data.get('request_update'):
        d = json.loads(player.current_dict) if player.current_dict else {}
        w = json.loads(player.current_word) if player.current_word else []
        return {
            pid: dict(
                performance=player.performance,
                mistakes=player.mistakes,
                work_seconds=player.work_seconds,
                dict=d,
                word=w,
                shuffle=False
            )
        }

    # ------------------------------------------------------------
    # STOP WORKING — final work_seconds is stored and nothing else changes
    # ------------------------------------------------------------
    if data.get("stop_work"):
        player.work_seconds = int(data["work_seconds"])
        player.stopped_work = True
        return {
            pid: dict(
                performance=player.performance,
                mistakes=player.mistakes,
                work_seconds=player.work_seconds,
                stopped_work=True,
                shuffle=False
            )
        }

    # ------------------------------------------------------------
    # PERFORMANCE update ⇒ increment AND refresh dict/word
    # ------------------------------------------------------------
    if 'performance' in data:
        player.performance = data['performance']

        d = build_random_dict()
        w = build_random_word(C.TASK_LENGTH)
        player.current_dict = json.dumps(d)
        player.current_word = json.dumps(w)

        return {
            pid: dict(
                performance=player.performance,
                mistakes=player.mistakes,
                work_seconds=player.work_seconds,
                dict=d,
                word=w,
                shuffle=True
            )
        }

    # ------------------------------------------------------------
    # Mistakes only (no word refresh)
    # ------------------------------------------------------------
    if 'mistakes' in data:
        player.mistakes = data['mistakes']

    # ------------------------------------------------------------
    # DEFAULT: just return current state
    # ------------------------------------------------------------
    d = json.loads(player.current_dict) if player.current_dict else {}
    w = json.loads(player.current_word) if player.current_word else []

    # ------------------------------------------------------------
    # ATTENTION CHECKS
    # ------------------------------------------------------------
    if data.get("attention_check_received"):
        player.attention_checks_received += 1
        return {player.id_in_group: dict()}

    if data.get("attention_check_failed"):
        player.attention_checks_failed += 1
        return {player.id_in_group: dict()}

    if data.get("attention_check_passed"):
        return {player.id_in_group: dict()}

    return {
        pid: dict(
            performance=player.performance,
            mistakes=player.mistakes,
            work_seconds=player.work_seconds,
            dict=d,
            word=w,
            shuffle=False
        )
    }

def get_timeout_seconds(player):
    config = player.session.config
    return config['work_length_seconds']


# PAGES
class PartStart(Page):
    @staticmethod
    def vars_for_template(player):
        config = player.session.config
        work_length_minutes = round(config['work_length_seconds']/60)
        return {
            'part': C.PARTS[player.round_number-1],
            'work_length_minutes': work_length_minutes,
        }


class Ideal(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        if player.round_number == 2:
            if player.participant.vars['treatment']:
                return ['ideal50', 'ideal60', 'ideal70', 'ideal80', 'ideal90', 'ideal100',
                        'ideal110', 'ideal120', 'ideal130', 'ideal140', 'ideal150']
            else:
                return ['ideal120']
        elif player.round_number == 6:
            if player.participant.vars['treatment']:
                return['lastideal_t']
            else:
                return['lastideal_c']
        else:
            return []

    @staticmethod
    def is_displayed(player):
        return player.round_number == 2 or player.round_number == 6

    @staticmethod
    def vars_for_template(player):
        treatment = player.participant.vars['treatment']
        payoff = base_constants.TRUE_PAYOFF
        config = player.session.config
        work_length_minutes = round(config['work_length_seconds']/60)
        return {
            'percent_ideal': base_constants.PERCENT_IDEAL,
            'treatment': treatment,
            'payoff': payoff,
            'work_length_minutes': work_length_minutes,
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number == 2:
            if player.participant.vars['treatment']:
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
            else:
                player.participant.vars['ideal'][8] = player.ideal120
                # Fill all other "ideal" fields with safe placeholder values
                # so blank=False validation never fails
                for i in [1, 2, 3, 4, 5, 6, 7, 9, 10, 11]:
                    setattr(player, f'ideal{50 + 10 * (i - 1)}', 999)
        elif player.round_number == 6:
            if player.participant.vars['treatment']:
                player.participant.vars['ideal'][12] = player.lastideal_t
                # Pre-fill the field not shown to avoid blank=False error
                player.lastideal_c = 999
            else:
                player.participant.vars['ideal'][12] = player.lastideal_c
                # Pre-fill the field not shown to avoid blank=False error
                player.lastideal_t = 999
        else:
            pass


class Predicted(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        if player.round_number == 2:
            if player.participant.vars['treatment']:
                return ['predicted50', 'predicted60', 'predicted70', 'predicted80', 'predicted90',
                        'predicted100', 'predicted110', 'predicted120', 'predicted130', 'predicted140',
                        'predicted150']
            else:
                return ['predicted120']
        elif player.round_number == 6:
            if player.participant.vars['treatment']:
                return ['lastpredicted_t']
            else:
                return ['lastpredicted_c']
        else:
            return []

    @staticmethod
    def is_displayed(player):
        return player.round_number == 2 or player.round_number == 6

    @staticmethod
    def vars_for_template(player):
        treatment = player.participant.vars['treatment']
        payoff = base_constants.TRUE_PAYOFF
        return {
            'treatment': treatment,
            'payoff': payoff,
        }

    @staticmethod
    def error_message(player, values):
        """Ensure predicted ≤ ideal for every payoff level."""

        payoff_map = {
            50: ('ideal50', 'predicted50'),
            60: ('ideal60', 'predicted60'),
            70: ('ideal70', 'predicted70'),
            80: ('ideal80', 'predicted80'),
            90: ('ideal90', 'predicted90'),
            100: ('ideal100', 'predicted100'),
            110: ('ideal110', 'predicted110'),
            120: ('ideal120', 'predicted120'),
            130: ('ideal130', 'predicted130'),
            140: ('ideal140', 'predicted140'),
            150: ('ideal150', 'predicted150'),
        }

        # Round 2
        if player.round_number == 2:

            # --- Treatment: multiple payoff levels ---
            if player.participant.vars['treatment']:
                for payoff, (ideal_field, pred_field) in payoff_map.items():

                    if pred_field in values:
                        ideal_val = getattr(player, ideal_field)
                        predicted_val = values[pred_field]

                        if predicted_val > ideal_val:
                            return (
                                f"For payoff {payoff}, your predicted tasks "
                                f"({predicted_val}) exceed your ideal tasks ({ideal_val})."
                            )

            # --- No treatment: only payoff 120 ---
            else:
                ideal_val = player.ideal120
                predicted_val = values['predicted120']

                if predicted_val > ideal_val:
                    return (
                        f"Your predicted number of tasks ({predicted_val}) "
                        f"cannot exceed your ideal number ({ideal_val})."
                    )

        # Round 6
        if player.round_number == 6:

            # --- Treatment ---
            if player.participant.vars['treatment']:
                ideal_val = player.lastideal_t
                predicted_val = values['lastpredicted_t']

            # --- No treatment ---
            else:
                ideal_val = player.lastideal_c
                predicted_val = values['lastpredicted_c']

            if predicted_val > ideal_val:
                return (
                    f"Your predicted number of tasks ({predicted_val}) "
                    f"cannot exceed your ideal number ({ideal_val})."
                )

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number == 2:
            if player.participant.vars['treatment']:
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
            else:
                player.participant.vars['predicted'][8] = player.predicted120
                # Fill all other "predicted" fields with safe placeholder values
                # so blank=False validation never fails
                for i in [1, 2, 3, 4, 5, 6, 7, 9, 10, 11]:
                    setattr(player, f'predicted{50 + 10 * (i - 1)}', 999)
        elif player.round_number == 6:
            if player.participant.vars['treatment']:
                player.participant.vars['predicted'][12] = player.lastpredicted_t
                player.lastpredicted_c = 999
            else:
                player.participant.vars['predicted'][12] = player.lastpredicted_c
                player.lastpredicted_t = 999
        else:
            pass


class Interval(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 2  # only shown in the first real round

    @staticmethod
    def vars_for_template(player):
        treatment = player.participant.vars['treatment']
        guess_about = base_constants.GUESS_ABOUT[treatment]
        return {
            'benefit_min': base_constants.BENEFIT_RANGE_MIN,
            'benefit_max': base_constants.BENEFIT_RANGE_MAX,
            'guess_about': guess_about,
            'treatment': treatment,
        }


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

    @staticmethod
    def get_form_fields(player):
        if player.participant.vars['treatment']:
            return ['belief_t']
        else:
            return ['belief_c']

    @staticmethod
    def vars_for_template(player):
        treatment = player.participant.vars['treatment']
        guess_about = base_constants.GUESS_ABOUT[treatment]
        interval_min = base_constants.BENEFIT_RANGE_MIN
        interval_max = base_constants.BENEFIT_RANGE_MAX
        return {
            'guess_about': guess_about,
            'interval_min': interval_min,
            'interval_max': interval_max,
            'treatment': treatment
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number > 1:
            if player.participant.vars['treatment']:
                player.participant.vars['belief'][player.round_number-1] = player.belief_t
                player.belief_c = 50
            else:
                player.participant.vars['belief'][player.round_number-1] = player.belief_c
                player.belief_t = 50

        if player.round_number == 6:
            prob_ideal = round((base_constants.PERCENT_IDEAL+C.PERCENT_IDEAL_PART5)/100, 2)
            player.do_ideal = bool(np.random.choice([True, False],
                                               p=[prob_ideal, 1-prob_ideal]))
            player.participant.vars['do_ideal'] = player.do_ideal

        # do either the ideal stated in the first round or in the last round:
            if player.do_ideal:
                player.ideal_index = int(np.random.choice([8, 12]))
                player.ideal_to_do = player.participant.vars['ideal'][player.ideal_index]
                player.participant.vars['ideal_to_do'] = player.ideal_to_do
                player.participant.vars['ideal_index'] = player.ideal_index


class Signal(Page):
    timeout_seconds = C.SIGNAL_TIMEOUT

    @staticmethod
    def is_displayed(player):
        # Your existing logic
        return 2 < player.round_number < 6

    @staticmethod
    def vars_for_template(player):

        # 1. If this is the FIRST time loading the page → store start_time
        if player.signal_start_time == 0:
            import time
            player.signal_start_time = time.time()

        # 2. Compute how much time has already passed
        import time
        now = time.time()
        elapsed = now - player.signal_start_time

        # 3. How many seconds REMAIN
        remaining = C.SIGNAL_TIMEOUT - elapsed
        if remaining < 0:
            remaining = 0

        treatment = player.participant.vars['treatment']
        guess_about = base_constants.GUESS_ABOUT[treatment]

        return dict(
            guess_about=guess_about,
            start_time=player.signal_start_time,
            total_time=C.SIGNAL_TIMEOUT,
            remaining_time=remaining,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        # This page always ends when the countdown hits zero
        pass

class Work(Page):  # in period 5, we tell the participants the number of tasks they have to do here
    @staticmethod
    def is_displayed(player):
        return player.round_number > 1

    @staticmethod
    def vars_for_template(player):
        config = player.session.config
        work_length_minutes = round(config['work_length_seconds'] / 60)

        if player.do_ideal:
            part_ideal_elicited = {8: 'first part', 12: 'last part'}
            treatment = player.participant.vars['treatment']
            guess_about = base_constants.GUESS_ABOUT[treatment]
            return {
                'ideal_to_do': player.ideal_to_do,
                'percent_ideal': base_constants.PERCENT_IDEAL,
                'part_ideal_elicited': part_ideal_elicited[player.ideal_index],
                'guess_about': guess_about,
                'work_length_minutes': work_length_minutes,
            }
        else:
            return {
                'work_length_minutes': work_length_minutes,
            }


class Task(Page):
    live_method = live_update_performance
    form_model = 'player'
    form_fields = ['performance', 'mistakes']

    get_timeout_seconds = get_timeout_seconds  # keep server cutoff

    @staticmethod
    def vars_for_template(player: Player):
        if player.task_start_time == 0:
            player.task_start_time = time.time()

        letters_per_word = C.TASK_LENGTH

        return dict(
            letters_per_word=letters_per_word,
            legend_list=list(range(26)),
            task_list=list(range(letters_per_word)),

            required_tasks=player.ideal_to_do,

            # JS timer
            task_start_time=player.task_start_time,          # unix seconds
            total_time=player.session.config['work_length_seconds']
        )

    @staticmethod
    def js_vars(player: Player):
        cfg = player.session.config
        return dict(
            required_tasks=player.ideal_to_do,
            timeout_seconds=cfg['work_length_seconds'],
            stopped_work=player.stopped_work,
            do_ideal=int(player.do_ideal),
            checks_received=player.attention_checks_received,
            checks_failed=player.attention_checks_failed,
        )


    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):

        total = player.session.config['work_length_seconds']

        # CASE 1: Stop working was pressed -> work_seconds already stored
        if player.work_seconds > 0:
            pass  # keep stored value

        # CASE 2: Stop working NOT pressed
        else:
            # They worked until timeout
            player.work_seconds = total

        # Nonwork seconds always the remainder
        player.nonwork_seconds = total - player.work_seconds

        # Cap performance
        if player.performance > player.ideal_to_do:
            player.performance = player.ideal_to_do

        p = player
        pp = p.participant
        idx = p.round_number - 1

        # Save round results
        pp.vars['actual'][idx] = p.performance
        pp.vars['mistakes'][idx] = p.mistakes
        pp.vars['work_seconds'][idx] = p.work_seconds
        pp.vars['nonwork_seconds'][idx] = p.nonwork_seconds
        pp.vars['attention_checks_received'][idx] = p.attention_checks_received
        pp.vars['attention_checks_failed'][idx] = p.attention_checks_failed

        print(
            'performance:', p.performance,
            'mistakes:', p.mistakes,
            'work seconds:', p.work_seconds,
            'nonwork seconds:', p.nonwork_seconds,
            'attention checks received:', p.attention_checks_received,
            'attention checks failed:', p.attention_checks_failed
        )


class Results(Page):
    pass


class Survey1(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 2

    form_model = 'player'
    form_fields = [
        'gender', 'age', 'employment', 'education', 'socialclass', 'children', 'mathgrade',
        'big5_openness1', 'big5_openness2', 'big5_openness3', 'big5_openness4'
    ]

    @staticmethod
    def before_next_page(player, timeout_happened):
        ppvars = player.participant.vars
        ppvars['gender'] = player.gender
        ppvars['age'] = player.age
        ppvars['employment'] = player.employment
        ppvars['education'] = player.education
        ppvars['socialclass'] = player.socialclass
        ppvars['children'] = player.children
        ppvars['mathgrade'] = player.mathgrade
        ppvars['big5_openness1'] = player.big5_openness1
        ppvars['big5_openness2'] = player.big5_openness2
        ppvars['big5_openness3'] = player.big5_openness3
        ppvars['big5_openness4'] = player.big5_openness4


class Survey2(Page):
    form_model = 'player'
    form_fields = ['digitspan_max_level']

    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

    @staticmethod
    def before_next_page(player, timeout_happened):
        ppvars = player.participant.vars
        ppvars['digitspan_max_level'] = player.digitspan_max_level


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
    def vars_for_template(player):
        thousand_points = cu(1000*player.session.config['real_world_currency_per_point'])
        return dict(
            risk_prefix='risk_',
            big5_prefix='big5_',
            thousand_points = thousand_points
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.vars['risk_choices'][0] = player.risk_0
        player.participant.vars['risk_choices'][1] = player.risk_50
        player.participant.vars['risk_choices'][2] = player.risk_100
        player.participant.vars['risk_choices'][3] = player.risk_150
        player.participant.vars['risk_choices'][4] = player.risk_200
        player.participant.vars['risk_choices'][5] = player.risk_250
        player.participant.vars['risk_choices'][6] = player.risk_300
        player.participant.vars['risk_choices'][7] = player.risk_350
        player.participant.vars['risk_choices'][8] = player.risk_400
        player.participant.vars['risk_choices'][9] = player.risk_450
        player.participant.vars['risk_choices'][10] = player.risk_500
        player.participant.vars['risk_choices'][11] = player.risk_550
        player.participant.vars['risk_choices'][12] = player.risk_600
        player.participant.vars['risk_choices'][13] = player.risk_650
        player.participant.vars['risk_choices'][14] = player.risk_700
        player.participant.vars['risk_choices'][15] = player.risk_750
        player.participant.vars['risk_choices'][16] = player.risk_800
        player.participant.vars['risk_choices'][17] = player.risk_850
        player.participant.vars['risk_choices'][18] = player.risk_900
        player.participant.vars['risk_choices'][19] = player.risk_950
        player.participant.vars['risk_choices'][20] = player.risk_1000
        player.participant.vars['big5_conscientious1'] = player.big5_conscientious1
        player.participant.vars['big5_conscientious2'] = player.big5_conscientious2
        player.participant.vars['big5_conscientious3'] = player.big5_conscientious3
        player.participant.vars['big5_extraversion1'] = player.big5_extraversion1
        player.participant.vars['big5_extraversion2'] = player.big5_extraversion2
        player.participant.vars['big5_extraversion3'] = player.big5_extraversion3


class Survey4(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 5

    form_model = 'player'
    form_fields = [
        'GPS_patience', 'GPS_altruism1', 'GPS_altruism2', 'GPS_timediscounting',
        'big5_agreeable1', 'big5_agreeable2', 'big5_agreeable3',
        'big5_neuroticism1', 'big5_neuroticism2', 'big5_neuroticism3'
    ]

    @staticmethod
    def before_next_page(player, timeout_happened):
        ppvars = player.participant.vars
        ppvars['GPS_patience'] = player.GPS_patience
        ppvars['GPS_altruism1'] = player.GPS_altruism1
        ppvars['GPS_altruism2'] = player.GPS_altruism2
        ppvars['GPS_timediscounting'] = player.GPS_timediscounting
        ppvars['big5_agreeable1'] = player.big5_agreeable1
        ppvars['big5_agreeable2'] = player.big5_agreeable2
        ppvars['big5_agreeable3'] = player.big5_agreeable3
        ppvars['big5_neuroticism1'] = player.big5_neuroticism1
        ppvars['big5_neuroticism2'] = player.big5_neuroticism2
        ppvars['big5_neuroticism3'] = player.big5_neuroticism3


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
        'ballsremembered3','screenshot', 'ai_integral'
    ]

    @staticmethod
    def before_next_page(player, timeout_happened):
        ppvars = player.participant.vars
        ppvars['BSCS_temptation'] = player.BSCS_temptation
        ppvars['BSCS_badhabits'] = player.BSCS_badhabits
        ppvars['BSCS_lazy'] = player.BSCS_lazy
        ppvars['BSCS_inappropriate'] = player.BSCS_inappropriate
        ppvars['BSCS_dobadthings'] = player.BSCS_dobadthings
        ppvars['BSCS_refusebad'] = player.BSCS_refusebad
        ppvars['BSCS_morediscipline'] = player.BSCS_morediscipline
        ppvars['BSCS_irondiscipline'] = player.BSCS_irondiscipline
        ppvars['BSCS_pleasure'] = player.BSCS_pleasure
        ppvars['BSCS_concentrating'] = player.BSCS_concentrating
        ppvars['BSCS_work'] = player.BSCS_work
        ppvars['BSCS_stop'] = player.BSCS_stop
        ppvars['BSCS_alternatives'] = player.BSCS_alternatives
        ppvars['averagetask'] = player.averagetask
        ppvars['ballsremembered1'] = player.ballsremembered1
        ppvars['ballsremembered2'] = player.ballsremembered2
        ppvars['ballsremembered3'] = player.ballsremembered3
        ppvars['screenshot'] = player.screenshot
        ppvars['ai_integral'] = player.ai_integral


        # Randomize and calculate final payment
        # Chosen part for payment for task and beliefs:
        parts = [i for i in range(C.NUM_ROUNDS)]
        parts_belief = parts[1:C.NUM_ROUNDS]
        player.task_chosen_part = random.choice(parts)
        player.belief_chosen_part = random.choice(parts_belief)

        # Payment for belief:
        belief_in_part = player.participant.vars['belief'][player.belief_chosen_part]
        prob = 1-((belief_in_part - base_constants.TRUE_PAYOFF)**2/base_constants.SCALING_PAR)
        player.prob = max(prob, 0)
        player.payment_for_belief = int(np.random.choice([base_constants.BELIEF_BONUS, 0], p=[player.prob, 1-player.prob]))

        # Payment for risk:
        risk_choices = [i for i in player.participant.vars['risk_choices'].keys()]
        player.risk_chosen = random.choice(risk_choices)
        player.choice_in_risk_chosen = player.participant.vars['risk_choices'][player.risk_chosen]
        if player.choice_in_risk_chosen == 0:
            player.risk_payment = C.RISK_FIXED[player.risk_chosen]
        else:
            player.risk_payment = random.choice([0, C.RISK_LARGE])


class Payment(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    form_model = 'player'
    form_fields = ['comments']

    @staticmethod
    def vars_for_template(player: Player):
        config = player.session.config
        chosen_part = C.PARTS[player.task_chosen_part]
        performance_in_part = player.participant.vars['actual'][player.task_chosen_part]
        not_done_ideal = False
        if player.task_chosen_part == 5 and player.participant.vars['do_ideal'] and performance_in_part < player.participant.vars['ideal_to_do']:
            not_done_ideal = True
            performance_to_pay = 0
        else:
            performance_to_pay = performance_in_part

        payoff_for_work = base_constants.TRUE_PAYOFF*performance_to_pay
        payoff_in_usd = cu(config['real_world_currency_per_point']*payoff_for_work)
        leisure_minutes = round((player.participant.vars['nonwork_seconds'][player.task_chosen_part])/60, 2)
        failed_attention_checks = (player.participant.vars['attention_checks_failed'][player.task_chosen_part] > 1)
        if not_done_ideal or failed_attention_checks:
            leisure_to_pay = 0
        else:
            leisure_to_pay = leisure_minutes
        leisure_payoff = round(leisure_to_pay * base_constants.FLAT_LEISURE_FEE, 2)
        leisure_payoff_usd = cu(round(config['real_world_currency_per_point']*leisure_payoff, 2))
        belief_chosen_part = C.PARTS[player.belief_chosen_part]
        belief_in_part = player.participant.vars['belief'][player.belief_chosen_part]
        chosen_risk_question = C.RISK_CHOICES[player.risk_chosen]
        choice_in_risk_chosen = C.RISK_OPTIONS[player.risk_chosen][player.choice_in_risk_chosen]
        payment_for_risk_usd = cu(player.risk_payment*config['real_world_currency_per_point'])
        payment_for_belief_usd = cu(config['real_world_currency_per_point']*player.payment_for_belief)

        total_payment = cu(config['participation_fee'] + payoff_in_usd + leisure_payoff_usd + payment_for_belief_usd + payment_for_risk_usd)

        treatment = player.participant.vars['treatment']
        guess_about = base_constants.GUESS_ABOUT[treatment]

        ppvars = player.participant.vars
        ppvars['task_chosen_part'] = player.task_chosen_part
        ppvars['prob'] = player.prob
        ppvars['belief_chosen_part'] = player.belief_chosen_part
        ppvars['payment_for_belief'] = player.payment_for_belief
        ppvars['risk_chosen'] = player.risk_chosen
        ppvars['risk_payment'] = player.risk_payment
        ppvars['choice_in_risk_chosen'] = player.choice_in_risk_chosen
        ppvars['total_payment'] = total_payment


        return {
            'completion_fee': config.get('participation_fee', ''),
            'chosen_part_index': player.task_chosen_part,
            'ideal_to_do': player.participant.vars['ideal_to_do'],
            'task_chosen_part': chosen_part,
            'performance_in_chosen_part': performance_in_part,
            'percent_ideal': base_constants.PERCENT_IDEAL,
            'do_ideal': ppvars['do_ideal'],
            'not_done_ideal': not_done_ideal,
            'failed_attention_checks': failed_attention_checks,
            'true_payoff': base_constants.TRUE_PAYOFF,
            'payoff_for_work': payoff_for_work,
            'payoff_for_work_usd': payoff_in_usd,
            'leisure_minutes': leisure_minutes,
            'leisure_payoff': leisure_payoff,
            'leisure_payoff_usd': leisure_payoff_usd,
            'belief_chosen_part': belief_chosen_part,
            'belief_in_chosen_part': belief_in_part,
            'payment_for_belief': player.payment_for_belief,
            'payment_for_belief_usd': payment_for_belief_usd,
            'payment_for_risk': player.risk_payment,
            'payment_for_risk_usd': payment_for_risk_usd,
            'chosen_risk_question': chosen_risk_question,
            'choice_in_risk_question': choice_in_risk_chosen,
            'total_payment': total_payment,
            'guess_about': guess_about,
            'treatment': treatment,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['comments'] = player.comments

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
    Ideal,
    Predicted,
    Interval,
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
    Payment,
    FinalPage
]


# Data export
def custom_export(players):
    # Collect keys for the export table
    fp = players[0]
    all_participant_vars = [v for v in fp.participant.vars.keys()]
    all_var_keys = []
    for var in all_participant_vars:
        if isinstance(fp.participant.vars[var], dict):
            for k in fp.participant.vars[var].keys():
                all_var_keys.append(f"{var}_{k}")
        else:
            all_var_keys.append(var)

    # Build header
    header = ['session_code',
              'work_length_seconds',
              'participant_code',
              'prolific_id',
              ] + all_var_keys
    yield header

    # Build data rows

    for p in players:
        participant = p.participant
        session = p.session

        if p.round_number == C.NUM_ROUNDS:

            row = [
                session.code,
                session.config.get('work_length_seconds', ''),
                participant.code,
                participant.label,
            ]

            for var in all_participant_vars:
                if isinstance(p.participant.vars[var], dict):
                    for key in p.participant.vars[var].keys():
                        row.append(p.participant.vars[var][key])
                else:
                    val = p.participant.vars.get(var, '')
                    row.append(val)

            yield row
