"""Completion, timing, final save and payment checks for a zero binding ideal."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from test_task_protocol import Player, protocol

ROOT = Path(__file__).parents[1]
APP = ast.parse((ROOT / 'study' / '__init__.py').read_text(encoding='utf-8'))


def source_function(name, cls=None):
    nodes = APP.body
    if cls:
        nodes = next(n for n in nodes if isinstance(n, ast.ClassDef) and n.name == cls).body
    fn = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == name)
    fn.decorator_list = []
    constants = NS(NUM_ROUNDS=6, PARTS={i: str(i) for i in range(6)},
                   RISK_CHOICES={0: 'test risk'}, RISK_OPTIONS={0: {0: 'test choice'}})
    base = NS(TRUE_PAYOFF=120, FLAT_LEISURE_FEE=70, PERCENT_IDEAL=2,
              GUESS_ABOUT={True: 'payoff per task', False: 'unrelated number'})
    env = dict(Player=Player, C=constants, base_constants=base, cu=lambda value: value,
               time=protocol.time)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), '<saved-source>', 'exec'), env)
    return env[name]


class ZeroIdealTests(unittest.TestCase):
    def setUp(self):
        self.player = Player()
        self.player.round_number = 6
        self.player.do_ideal = True
        self.player.ideal_to_do = 0
        self.player.participant = NS(vars={
            'actual': {i: 0 for i in range(6)}, 'mistakes': {i: 0 for i in range(6)},
            'work_seconds': {i: 0 for i in range(6)}, 'nonwork_seconds': {i: 0 for i in range(6)},
            'do_ideal': True, 'ideal_to_do': 0, 'treatment': True, 'belief': {0: 100},
        }, code='zero-test', label='synthetic')
        self.player.session.code = 'synthetic'
        self.now = 1005

    def send(self, data=None):
        with patch.object(protocol.time, 'time', return_value=self.now):
            return protocol.handle_task_message(
                self.player, data or {'init': True}, bonus=False, task_length=4, bonus_tasks=5,
                build_dict=lambda: dict(A=101, B=102, C=103, D=104),
                build_word=lambda _: list('ABCD'),
            )[1]

    def save(self):
        source_function('before_next_page', 'Task')(self.player, False)

    def test_zero_initial_load_is_complete_and_has_zero_work_despite_late_init(self):
        state = self.send()
        self.assertTrue(state['completed'])
        self.assertTrue(state['stopped_work'])
        self.assertEqual((state['performance'], state['work_seconds'], state['performance_in_time']), (0, 0, 0))
        self.assertEqual(state['remaining_seconds'], 475)

    def test_first_page_render_prepares_zero_without_waiting_for_live_message(self):
        self.player.task_start_time = 0
        protocol.prepare_task(self.player, 1000)
        self.assertEqual((self.player.task_start_time, self.player.work_seconds, self.player.stopped_work), (1000, 0, True))
        protocol.prepare_task(self.player, 1200)
        self.assertEqual((self.player.task_start_time, self.player.work_seconds), (1000, 0))

    def test_zero_refresh_keeps_zero_and_original_deadline(self):
        self.send()
        self.now = 1200
        state = self.send()
        self.assertEqual(state['remaining_seconds'], 280)
        self.assertEqual(state['work_seconds'], 0)
        self.now = 1500
        state = self.send()
        self.assertTrue(state['completed'])
        self.assertEqual((state['remaining_seconds'], state['work_seconds']), (0, 0))

    def test_zero_cannot_be_increased_by_a_valid_answer(self):
        state = self.send()
        result = self.send(dict(task_id=state['task_id'], answer_token=state['answer_token'],
                                answer=[101, 102, 103, 104]))
        self.assertEqual(result['performance'], 0)
        self.assertEqual(result['rejected'], 'work_finished')

    def test_zero_final_save_preserves_zero_and_full_leisure_at_both_durations(self):
        for total in (30, 480):
            self.player.session.config['work_length_seconds'] = total
            self.send()
            self.save()
            self.assertEqual((self.player.performance, self.player.work_seconds, self.player.nonwork_seconds), (0, 0, total))
            saved = self.player.participant.vars
            self.assertEqual((saved['actual'][5], saved['work_seconds'][5], saved['nonwork_seconds'][5]), (0, 0, total))
            self.assertEqual(saved['performance_in_time_5'], 0)

    def test_zero_export_and_payment_preserve_zero(self):
        self.send()
        self.save()
        rows = list(source_function('custom_export')([self.player]))
        values = dict(zip(rows[0], rows[1]))
        self.assertEqual((values['actual_5'], values['work_seconds_5'], values['nonwork_seconds_5']), (0, 0, 480))
        self.player.session.config.update(real_world_currency_per_point=.0015, participation_fee=11)
        self.player.task_chosen_part = 5
        self.player.belief_chosen_part = self.player.risk_chosen = self.player.choice_in_risk_chosen = 0
        self.player.risk_payment = self.player.payment_for_belief = self.player.prob = 0
        for treatment in (True, False):
            self.player.participant.vars['treatment'] = treatment
            result = source_function('vars_for_template', 'Payment')(self.player)
            self.assertEqual((result['performance_to_pay'], result['payoff_for_work'], result['leisure_minutes']), (0, 0, 8))
            self.assertAlmostEqual(result['leisure_payoff_usd'], .84)
            self.assertAlmostEqual(result['total_payment'], 11.84)

    def test_valid_zero_stop_is_not_replaced_by_full_work(self):
        self.player.do_ideal = False
        self.player.stopped_work = True
        self.save()
        self.assertEqual((self.player.work_seconds, self.player.nonwork_seconds), (0, 480))

    def test_unstopped_trial_and_free_work_still_record_full_work(self):
        for round_number in (1, 2):
            self.player.round_number = round_number
            self.player.do_ideal = False
            self.player.stopped_work = False
            self.player.work_seconds = 0
            self.save()
            self.assertEqual((self.player.work_seconds, self.player.nonwork_seconds), (480, 0))

    def test_positive_ideal_stays_open_until_solved_and_keeps_recorded_stop(self):
        self.player.ideal_to_do = 2
        state = self.send()
        self.assertFalse(state['completed'])
        self.now = 1490
        self.assertFalse(self.send()['completed'])
        for _ in range(2):
            state = self.send(dict(task_id=state['task_id'], answer_token=state['answer_token'],
                                   answer=[101, 102, 103, 104]))
        self.save()
        self.assertEqual((self.player.performance, self.player.work_seconds, self.player.nonwork_seconds), (2, 480, 0))
        self.assertEqual(self.player.participant.vars['performance_in_time_5'], 0)

    def test_positive_ideal_completed_in_first_second_keeps_valid_zero_time(self):
        self.player.ideal_to_do = 1
        self.now = 1000.2
        state = self.send()
        self.send(dict(task_id=state['task_id'], answer_token=state['answer_token'], answer=[101, 102, 103, 104]))
        self.save()
        self.assertEqual((self.player.performance, self.player.work_seconds, self.player.nonwork_seconds), (1, 0, 480))

    def test_completed_ideal_timeout_uses_original_remaining_duration(self):
        timeout = source_function('get_timeout_seconds', 'Task')
        with patch.object(protocol.time, 'time', return_value=1200):
            self.assertEqual(timeout(self.player), 280)
        self.player.ideal_to_do = 1
        self.assertIsNone(timeout(self.player), 'unfinished ideal must still allow overtime')


if __name__ == '__main__':
    unittest.main()
