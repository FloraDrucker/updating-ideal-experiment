from otree.api import *
from . import C
from . import *


# ======================================================
# 🔧 HELPERS
# ======================================================

def solve_word(enc_dict, word):
    """Return the correct encoding of a word."""
    return [enc_dict[l] for l in word]


def play_encryption_task(bot, n_tasks=20, overtime=False):
    """
    Plays the live encryption task by directly calling the live_method function.
    This is compatible with oTree versions whose Bot API has no live_send().
    Includes periodic page refreshes to simulate real participant behavior.

    Args:
        bot: The bot player
        n_tasks: Number of tasks to complete
        overtime: If True, backdate task_start_time so every answer arrives after the
                  deadline, simulating a do_ideal participant who finishes in overtime.
    """
    import time
    player = bot.player

    if overtime:
        total = player.session.config['work_length_seconds']
        player.task_start_time = time.time() - total - 10

    # INIT
    resp = live_update_performance(player, {'init': True})
    payload = list(resp.values())[0]

    performance = payload.get('performance', 0)
    mistakes = payload.get('mistakes', 0)

    # Exercise the same answer/token protocol as the browser.
    for task_num in range(n_tasks):
        if payload.get('completed'):
            break
        resp = live_update_performance(player, dict(
            task_id=payload['task_id'], answer_token=payload['answer_token'],
            answer=solve_word(payload['encryption_dict'], payload['word_list']),
        ))
        payload = list(resp.values())[0]
        if task_num % 2 == 1:
            resp = live_update_performance(player, {'request_update': True})
            payload = list(resp.values())[0]

    # Server records receipt time. Bots do not pretend that wall-clock time elapsed.
    live_update_performance(player, {'stop_work': True})


def play_bonus_task(bot):
    """Complete all C.BONUS_TASKS bonus encryption tasks via the bonus live method."""
    player = bot.player
    resp = live_update_bonus_performance(player, {'init': True})
    payload = list(resp.values())[0]
    for _ in range(C.BONUS_TASKS):
        if payload.get('completed'):
            break
        resp = live_update_bonus_performance(player, dict(
            task_id=payload['task_id'], answer_token=payload['answer_token'],
            answer=solve_word(payload['encryption_dict'], payload['word_list']),
        ))
        payload = list(resp.values())[0]


# ======================================================
# 🧠 ANSWER BLOCKS
# ======================================================

def ideal_zero_answers_for_round(bot):
    """Ideal answers where ideal120=0; all other payoff levels stay at 10."""
    if bot.round_number == 2:
        return dict(
            ideal50=10, ideal60=10, ideal70=10, ideal80=10,
            ideal90=10, ideal100=10, ideal110=10, ideal120=0,
            ideal130=10, ideal140=10, ideal150=10,
        )
    if bot.round_number == 6:
        if bot.player.participant.vars['treatment']:
            return dict(lastideal_t=0)
        else:
            return dict(lastideal_c=0)
    return {}


def predicted_zero_answers_for_round(bot):
    """Predicted answers consistent with ideal120=0 (predicted must not exceed ideal)."""
    if bot.round_number == 2:
        return dict(
            predicted50=8, predicted60=8, predicted70=8, predicted80=8,
            predicted90=8, predicted100=8, predicted110=8, predicted120=0,
            predicted130=8, predicted140=8, predicted150=8,
        )
    if bot.round_number == 6:
        if bot.player.participant.vars['treatment']:
            return dict(lastpredicted_t=0)
        else:
            return dict(lastpredicted_c=0)
    return {}


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
        task_like=4,
        task_more=False,
        ai_integral=4,
    )


def survey5_bonus_answers():
    """Survey5 answers with task_more=True so BonusTask is displayed."""
    answers = survey5_answers().copy()
    answers['task_more'] = True
    return answers


def ideal_n_answers_for_round(bot, n):
    """Ideal answers where every payoff level is set to n tasks."""
    if bot.round_number == 2:
        return dict(
            ideal50=n, ideal60=n, ideal70=n, ideal80=n,
            ideal90=n, ideal100=n, ideal110=n, ideal120=n,
            ideal130=n, ideal140=n, ideal150=n,
        )
    if bot.round_number == 6:
        if bot.player.participant.vars['treatment']:
            return dict(lastideal_t=n)
        else:
            return dict(lastideal_c=n)
    return {}


def predicted_n_answers_for_round(bot, n):
    """Predicted answers where every payoff level is set to n tasks (≤ ideal)."""
    if bot.round_number == 2:
        return dict(
            predicted50=n, predicted60=n, predicted70=n, predicted80=n,
            predicted90=n, predicted100=n, predicted110=n, predicted120=n,
            predicted130=n, predicted140=n, predicted150=n,
        )
    if bot.round_number == 6:
        if bot.player.participant.vars['treatment']:
            return dict(lastpredicted_t=n)
        else:
            return dict(lastpredicted_c=n)
    return {}


# ======================================================
# 🤖 BOT
# ======================================================

class PlayerBot(Bot):
    cases = [
        'default', 'ideal_zero', 'stop_immediately', 'excluded_timeout',
        'ideal_finish_early', 'ideal_overtime', 'bonus_tasks', 'early_exclusion',
    ]

    def play_round(self):

        # 1) Interval (only round 1; shown before PartStart)
        if self.round_number == 1:
            if self.player.participant.vars['treatment']:
                yield Interval, dict(belief_t=100)
            else:
                yield Interval, dict(belief_c=100)

        # Excluded[1]: before PartStart; shown from round 3 onwards for early_exclusion
        if self.case == 'early_exclusion' and self.round_number > 2:
            yield Submission(Excluded, check_html=False)

        # 2) PartStart (always)
        yield PartStart

        # 3) Performance (displayed only if round_number > 2)
        if self.round_number > 2:
            yield Performance

        # 4) Belief (displayed only if round_number > 2)
        if self.round_number > 2:
            if self.player.participant.vars['treatment']:
                yield Belief, dict(belief_t=110)
            else:
                yield Belief, dict(belief_c=110)

        # Excluded[5]: after Belief; shown from round 3 onwards for early_exclusion
        if self.case == 'early_exclusion' and self.round_number > 2:
            yield Submission(Excluded, check_html=False)

        # 5) Ideal (round 2 and 6)
        if self.round_number in [2, 6]:
            if self.case == 'ideal_zero':
                yield Ideal, ideal_zero_answers_for_round(self)
            elif self.case in ('ideal_finish_early', 'ideal_overtime') and self.round_number == 6:
                yield Ideal, ideal_n_answers_for_round(self, 3)
            else:
                yield Ideal, ideal_answers_for_round(self)

        # Excluded[7]: after Ideal; shown from round 3 onwards for early_exclusion
        if self.case == 'early_exclusion' and self.round_number > 2:
            yield Submission(Excluded, check_html=False)

        # 6) Predicted (round 2 and 6)
        if self.round_number in [2, 6]:
            if self.case == 'ideal_zero' and self.round_number == 6:
                # Force do_ideal so that Predicted.before_next_page resolves
                # ideal_to_do from ideal_index=8 (ideal120), which was entered as 0
                # in round 2. This simulates the 2 % of participants who must do
                # exactly their stated ideal number of tasks.
                ppvars = self.player.participant.vars
                ppvars['do_ideal'] = True
                ppvars['ideal_index'] = 8
                yield Predicted, predicted_zero_answers_for_round(self)
            elif self.case == 'ideal_zero':
                yield Predicted, predicted_zero_answers_for_round(self)
            elif self.case in ('ideal_finish_early', 'ideal_overtime') and self.round_number == 6:
                # Force do_ideal with ideal_index=12 (round-6 last ideal = 3 tasks)
                ppvars = self.player.participant.vars
                ppvars['do_ideal'] = True
                ppvars['ideal_index'] = 12
                yield Predicted, predicted_n_answers_for_round(self, 3)
            else:
                yield Predicted, predicted_answers_for_round(self)

        # Excluded[9]: after Predicted; shown from round 3 onwards for early_exclusion
        if self.case == 'early_exclusion' and self.round_number > 2:
            yield Submission(Excluded, check_html=False)

        # 7) Signal (rounds 3-5)
        if 2 < self.round_number < 6:
            yield Signal

        # 8) Work (displayed only if round_number > 1)
        if self.round_number > 1:
            yield Work

        # 9) Task (live page)
        # Bot behaviour per round:
        # Round 1:                               Full work (20 tasks)
        # Round 2 (default/most cases):          Stop after 2 tasks
        # Round 2 (stop_immediately):            Stop immediately without solving any task
        # Round 3:                               Full work (20 tasks)
        # Round 4:                               Stop without solving a task
        # Rounds 5-6 (most cases):               Full work (20 tasks)
        # Round 6 (ideal_zero):                  ideal_to_do=0, stop immediately
        # Round 6 (ideal_finish_early):          3 tasks, all within deadline
        # Round 6 (ideal_overtime):              3 tasks, all past deadline (backdated start)
        if self.case == 'ideal_zero' and self.round_number == 6:
            play_encryption_task(self, n_tasks=0)
        elif self.case == 'ideal_finish_early' and self.round_number == 6:
            play_encryption_task(self, n_tasks=3)
        elif self.case == 'ideal_overtime' and self.round_number == 6:
            play_encryption_task(self, n_tasks=3, overtime=True)
        elif self.round_number == 1:
            play_encryption_task(self, n_tasks=20)
        elif self.round_number == 2:
            if self.case == 'stop_immediately':
                play_encryption_task(self, n_tasks=0)
            else:
                play_encryption_task(self, n_tasks=2)
        elif self.round_number == 3:
            play_encryption_task(self, n_tasks=20)
        elif self.round_number == 4:
            play_encryption_task(self, n_tasks=0)
        elif self.round_number in [5, 6]:
            play_encryption_task(self, n_tasks=20)

        # Submit the Task page
        yield Submission(Task, check_html=False)

        # Assertions after Task -----------------------------------------------

        if self.case == 'ideal_zero' and self.round_number == 6:
            expect(self.player.do_ideal, True)
            expect(self.player.ideal_to_do, 0)
            expect(self.player.performance, 0)

        if self.case == 'stop_immediately' and self.round_number == 2:
            expect(self.player.stopped_work, True)
            expect(self.player.performance, 0)

        # ideal_finish_early: completes exactly ideal_to_do tasks within the deadline
        if self.case == 'ideal_finish_early' and self.round_number == 6:
            expect(self.player.do_ideal, True)
            expect(self.player.ideal_to_do, 3)
            expect(self.player.performance, 3)
            expect(self.player.stopped_work, True)
            expect(self.player.field_maybe_none('performance_in_time'), 3)

        # ideal_overtime: completes all tasks but none fall within the original deadline
        if self.case == 'ideal_overtime' and self.round_number == 6:
            expect(self.player.do_ideal, True)
            expect(self.player.ideal_to_do, 3)
            expect(self.player.performance, 3)
            expect(self.player.stopped_work, True)
            expect(self.player.field_maybe_none('performance_in_time'), 0)

        # 10) EndOfWork
        yield EndOfWork

        # 11) Survey1 (round 2)
        if self.round_number == 2:
            if self.case == 'early_exclusion':
                # Full timeout with no fields filled → excluded=True
                yield Submission(Survey1, {}, check_html=False, timeout_happened=True)
                expect(self.player.participant.vars['excluded'], True)
                expect(self.player.participant.vars['exclusion_page'], 'Survey1')
                for _ in range(5):  # Excluded[15,17,19,21,23]
                    yield Submission(Excluded, check_html=False)
            else:
                yield Survey1, survey1_answers()

        # Excluded[15]: after Survey1 position; shown from round 3 onwards for early_exclusion
        if self.case == 'early_exclusion' and self.round_number >= 3:
            yield Submission(Excluded, check_html=False)

        # 12) Survey2 (round 3)
        if self.round_number == 3:
            yield Survey2, survey2_answers()

        # Excluded[17]: after Survey2 position
        if self.case == 'early_exclusion' and self.round_number >= 3:
            yield Submission(Excluded, check_html=False)

        # 13) Survey3 (round 4)
        if self.round_number == 4:
            yield Survey3, survey3_answers()

        # Excluded[19]: after Survey3 position
        if self.case == 'early_exclusion' and self.round_number >= 3:
            yield Submission(Excluded, check_html=False)

        # 14) Survey4 (round 5)
        if self.round_number == 5:
            yield Survey4, survey4_answers()

        # Excluded[21]: after Survey4 position
        if self.case == 'early_exclusion' and self.round_number >= 3:
            yield Submission(Excluded, check_html=False)

        # 15) Round 6: surveys and payment
        if self.round_number == 6:
            if self.case == 'excluded_timeout':
                # Simulate a full Survey5 timeout: no fields filled → excluded
                yield Submission(Survey5, {}, check_html=False, timeout_happened=True)
                yield Submission(Excluded, check_html=False)
                expect(self.player.participant.vars['excluded'], True)
                expect(self.player.participant.vars['exclusion_reason'], 'incomplete_timeout')
            elif self.case == 'early_exclusion':
                # Already excluded from round 2; still sees Survey5 (no exclusion guard there)
                yield Survey5, survey5_answers()
                yield Submission(Excluded, check_html=False)  # Excluded[23]
            elif self.case == 'bonus_tasks':
                yield Survey5, survey5_bonus_answers()
                play_bonus_task(self)
                yield Submission(BonusTask, check_html=False)
                expect(self.player.bonus_performance, C.BONUS_TASKS)
                yield Submission(Payment, dict(comments="bot test"), check_html=False)
                yield Submission(FinalPage, check_html=False)
            else:
                yield Survey5, survey5_answers()
                yield Submission(Payment, dict(comments="bot test"), check_html=False)
                yield Submission(FinalPage, check_html=False)

        # Excluded[23]: after Survey5 position; rounds 3-5 for early_exclusion
        # (round 6 handles its own Excluded[23] in the block above)
        if self.case == 'early_exclusion' and self.round_number in [3, 4, 5]:
            yield Submission(Excluded, check_html=False)

