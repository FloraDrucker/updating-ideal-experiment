from otree.api import *
from . import C
from . import *


# ======================================================
# 🔧 HELPERS
# ======================================================

def solve_word(enc_dict, word):
    """Return the correct encoding of a word."""
    return [enc_dict[l] for l in word]


def play_encryption_task(bot, n_tasks=3, work_seconds=5):
    """
    Plays the live encryption task by directly calling the live_method function.
    This is compatible with oTree versions whose Bot API has no live_send().
    Includes periodic page refreshes to simulate real participant behavior.
    """

    player = bot.player

    # INIT
    resp = live_update_performance(player, {'init': True})
    payload = list(resp.values())[0]

    performance = payload.get('performance', 0)
    mistakes = payload.get('mistakes', 0)

    # solve a few tasks: each "performance" update refreshes dict/word
    for task_num in range(n_tasks):
        enc_dict = payload['encryption_dict']
        word = payload['word_list']

        # compute solution (not sent anywhere yet, but exercises mapping logic)
        solve_word(enc_dict, word)

        performance += 1
        resp = live_update_performance(player, {'performance': performance})
        payload = list(resp.values())[0]
        
        # Simulate page refresh every other task (real participants may refresh)
        if task_num % 2 == 1:
            resp = live_update_performance(player, {'request_update': True, 'client_performance': performance, 'client_mistakes': mistakes})
            payload = list(resp.values())[0]

    # STOP WORK
    live_update_performance(player, {'stop_work': True, 'work_seconds': work_seconds})


# ======================================================
# 🧠 ANSWER BLOCKS
# ======================================================

def ideal_answers_for_round(bot):
    # Round 2: all 11 fields
    if bot.round_number == 2:
        return dict(
            ideal50=10, ideal60=10, ideal70=10, ideal80=10,
            ideal90=10, ideal100=10, ideal110=10, ideal120=10,
            ideal130=10, ideal140=10, ideal150=10,
        )

    # Round 6: only one field depending on treatment
    if bot.round_number == 6:
        if bot.player.participant.vars['treatment']:
            return dict(lastideal_t=10)
        else:
            return dict(lastideal_c=10)

    return {}


def predicted_answers_for_round(bot):
    # Round 2: all 11 fields
    if bot.round_number == 2:
        return dict(
            predicted50=8, predicted60=8, predicted70=8, predicted80=8,
            predicted90=8, predicted100=8, predicted110=8, predicted120=8,
            predicted130=8, predicted140=8, predicted150=8,
        )

    # Round 6: only one field depending on treatment
    if bot.round_number == 6:
        if bot.player.participant.vars['treatment']:
            return dict(lastpredicted_t=8)
        else:
            return dict(lastpredicted_c=8)

    return {}


def survey1_answers():
    return dict(
        gender=0,
        age=30,
        employment=3,
        education=4,
        socialclass=2,
        children=0,
        mathgrade='B',
        big5_openness1=4,
        big5_openness2=4,
        big5_openness3=4,
        big5_openness4=4,
    )


def survey2_answers():
    return dict(digitspan_max_level=5)


def survey3_answers():
    return dict(
        risk_0=0, risk_50=0, risk_100=0, risk_150=0,
        risk_200=0, risk_250=0, risk_300=0, risk_350=0,
        risk_400=0, risk_450=0, risk_500=0, risk_550=0,
        risk_600=0, risk_650=0, risk_700=0, risk_750=0,
        risk_800=0, risk_850=0, risk_900=0, risk_950=0,
        risk_1000=0,

        # NOTE: Survey3 in your app does NOT ask BSCS_* fields.
        # It asks risk_* and big5_conscientious/extraversion fields.
        big5_conscientious1=4,
        big5_conscientious2=4,
        big5_conscientious3=4,
        big5_extraversion1=4,
        big5_extraversion2=4,
        big5_extraversion3=4,
    )


def survey4_answers():
    # NOTE: In your app, Survey4 is GPS + big5_agreeable/neuroticism (not averaging/balls).
    return dict(
        GPS_patience=5,
        GPS_altruism1=5,
        GPS_altruism2=200,
        GPS_timediscounting=5,
        big5_agreeable1=4,
        big5_agreeable2=4,
        big5_agreeable3=4,
        big5_neuroticism1=4,
        big5_neuroticism2=4,
        big5_neuroticism3=4,
    )


def survey5_answers():
    # NOTE: In your app, Survey5 is BSCS + averagetask + balls + screenshot + ai_integral.
    return dict(
        BSCS_temptation=3,
        BSCS_badhabits=3,
        BSCS_lazy=3,
        BSCS_inappropriate=3,
        BSCS_dobadthings=3,
        BSCS_refusebad=3,
        BSCS_morediscipline=3,
        BSCS_irondiscipline=3,
        BSCS_pleasure=3,
        BSCS_concentrating=3,
        BSCS_work=3,
        BSCS_stop=3,
        BSCS_alternatives=3,
        averagetask=111,
        ballsremembered1=0,
        ballsremembered2=0,
        ballsremembered3=0,
        screenshot=False,
        ai_integral=4,
    )


# ======================================================
# 🤖 BOT
# ======================================================

class PlayerBot(Bot):

    def play_round(self):

        # 1) Interval (only round 1; shown before PartStart)
        if self.round_number == 1:
            if self.player.participant.vars['treatment']:
                yield Interval, dict(belief_t=100)
            else:
                yield Interval, dict(belief_c=100)

        # 2) PartStart (always)
        yield PartStart

        # 3) Performance (displayed only if round_number > 1)
        if self.round_number > 1:
            yield Performance

        # 4) Belief (displayed only if round_number > 2)
        if self.round_number > 2:
            if self.player.participant.vars['treatment']:
                yield Belief, dict(belief_t=110)
            else:
                yield Belief, dict(belief_c=110)

        # 5) Ideal (round 2 and 6)
        if self.round_number in [2, 6]:
            yield Ideal, ideal_answers_for_round(self)

        # 6) Predicted (round 2 and 6)
        if self.round_number in [2, 6]:
            yield Predicted, predicted_answers_for_round(self)

        # 7) Signal (rounds 3-5)
        if 2 < self.round_number < 6:
            yield Signal

        # 8) Work (displayed only if round_number > 1 in your code,
        # but it's safe to also gate it here)
        if self.round_number > 1:
            yield Work

        # 9) Task (live page)
        # Play the task first to populate performance and mistakes
        play_encryption_task(self, n_tasks=3, work_seconds=5)
        
        # Submit the Task page with correct performance values
        yield Submission(Task, dict(performance=self.player.performance, mistakes=self.player.mistakes), check_html=False)

        # 10) EndOfWork
        yield EndOfWork

        # 11-15) Surveys depend on round number
        if self.round_number == 2:
            yield Survey1, survey1_answers()

        if self.round_number == 3:
            yield Survey2, survey2_answers()

        if self.round_number == 4:
            yield Survey3, survey3_answers()

        if self.round_number == 5:
            yield Survey4, survey4_answers()

        if self.round_number == 6:
            yield Survey5, survey5_answers()
            yield Submission(Payment, dict(comments="bot test"), check_html=False)
            yield Submission(FinalPage, check_html=False)

