from otree.api import *
from . import C
from . import *


# Wrong answers for the comprehension questions (any option except the solution)
WRONG = dict(
    q1='No, because some balls are never shown.',
    q2='It will be based on your average performance across all parts.',
    q3=10,
    q4t='Always guess a very high number.',
    q4c='Always guess a very high number.',
    q5t='It is the highest number out of the 60 balls shown.',
    q5c='It is the highest number out of the 60 balls shown.',
    q6t='Yes, for each part only the balls I see in this part matter for calculating the payoff per task.',
    q6c='Yes, for each part only the balls I see in this part matter for calculating the chosen number.',
)


def comprehension_answers(bot, wrong=()):
    """Correct answers, except the questions listed in `wrong` (e.g. ['q3', 'q6'])."""
    suffix = 't' if bot.player.treatment else 'c'
    names = ['q1', 'q2', 'q3', 'q4' + suffix, 'q5' + suffix, 'q6' + suffix]
    answers = {}
    for name in names:
        answers[name] = WRONG[name] if name[:2] in wrong else C.SOLUTIONS[name]
    return answers


class PlayerBot(Bot):
    # Must list the same case names, in the same order, as study/tests.py,
    # so that both apps play the same scenario for a participant.
    cases = [
        'default', 'ideal_zero', 'stop_immediately', 'excluded_timeout',
        'ideal_finish_early', 'ideal_overtime', 'bonus_tasks', 'early_exclusion',
        'comprehension_retry', 'comprehension_fail', 'no_consent', 'survey2_timeout',
    ]

    def play_round(self):

        yield Welcome
        yield EncryptionTask
        yield Instructions

        suffix = 't' if self.player.treatment else 'c'

        if self.case == 'comprehension_fail':
            # 4 of 6 wrong on the first attempt -> excluded immediately
            yield ComprehensionCheck, comprehension_answers(self, wrong=['q1', 'q2', 'q3', 'q6'])
            yield Submission(Excluded, check_html=False)
            pv = self.participant.vars
            expect(pv['excluded'], True)
            expect(pv['exclusion_reason'], 'comprehension_failed')
            expect(pv['exclusion_page'], 'ComprehensionCheck')
            expect(pv['wrong_questions_attempt1'], 'q1,q2,q3,q6' + suffix)
            return

        if self.case == 'comprehension_retry':
            # 2 wrong (incl. the new question 6), then 1 wrong -> correct answers shown, continue
            yield ComprehensionCheck, comprehension_answers(self, wrong=['q3', 'q6'])
            yield ComprehensionCheck, comprehension_answers(self, wrong=['q6'])
            yield ShowCorrectAnswers
            pv = self.participant.vars
            expect(pv['excluded'], False)
            expect(pv['wrong_questions_attempt1'], 'q3,q6' + suffix)
            expect(pv['wrong_questions_attempt2'], 'q6' + suffix)
            expect(pv['total_wrong'], 3)
        else:
            yield ComprehensionCheck, comprehension_answers(self)

        if self.case == 'no_consent':
            # Declines participation -> NoConsent page, study ends there
            yield Consent, dict(consent=False, consent_no_ai=True)
            expect(self.participant.vars['consent'], False)
            expect(self.participant.vars['excluded'], False)
            return

        yield Consent, dict(consent=True, consent_no_ai=True)
