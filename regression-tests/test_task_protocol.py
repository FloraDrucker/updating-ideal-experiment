"""Run: .venv\Scripts\python.exe -m unittest discover -s regression-tests -v"""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('task_protocol', Path(__file__).parents[1] / 'study' / 'task_protocol.py')
protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol)


class Player:
    def __init__(self):
        self.id_in_group = 1
        self.round_number = 2
        self.session = SimpleNamespace(config={'work_length_seconds': 480})
        self.task_start_time = 1000
        self.performance = self.mistakes = self.bonus_performance = self.bonus_mistakes = 0
        self.work_seconds = 0
        self.performance_in_time = None
        self.stopped_work = self.do_ideal = False
        self.ideal_to_do = 999
        self.task_protocol = self.bonus_task_protocol = ''

    def field_maybe_none(self, name):
        return getattr(self, name, None)


class TaskProtocolTests(unittest.TestCase):
    def setUp(self):
        self.player = Player()
        self.now = 1001

    def send(self, data, bonus=False):
        with patch.object(protocol.time, 'time', return_value=self.now):
            return protocol.handle_task_message(
                self.player, data, bonus=bonus, task_length=4, bonus_tasks=5,
                build_dict=lambda: dict(A=101, B=102, C=103, D=104),
                build_word=lambda _: list('ABCD'),
            )[1]

    def answer(self, state, values=None):
        return dict(task_id=state['task_id'], answer_token=state['answer_token'],
                    answer=[101, 102, 103, 104] if values is None else values)

    def test_correct_answer_and_retry_count_once(self):
        initial = self.send({'init': True})
        message = self.answer(initial)
        accepted = self.send(message)
        duplicate = self.send(message)
        self.assertEqual((accepted['performance'], duplicate['performance']), (1, 1))
        self.assertEqual(duplicate['rejected'], 'stale_attempt')
        self.assertNotEqual(initial['task_id'], accepted['task_id'])

    def test_incorrect_answer_is_checked_and_retry_is_not_another_mistake(self):
        state = self.send({'init': True})
        message = self.answer(state, [0, 0, 0, 0])
        first, retry = self.send(message), self.send(message)
        self.assertEqual(first['errors'], 4)
        self.assertEqual((first['mistakes'], retry['mistakes']), (1, 1))
        self.assertEqual(first['performance'], 0)
        self.assertEqual(first['task_id'], state['task_id'])
        self.assertEqual(self.send(self.answer(first))['performance'], 1)

    def test_legacy_totals_init_and_snapshot_cannot_inflate(self):
        for message in ({'performance': 900}, {'mistakes': 900},
                        {'init': True, 'client_performance': 900, 'client_mistakes': 900},
                        {'record_in_time': True, 'performance': 900}):
            state = self.send(message)
            self.assertEqual((state['performance'], state['mistakes'], state['performance_in_time']), (0, 0, 0))

    def test_forged_task_id_and_attempt_token_cannot_count(self):
        state = self.send({'init': True})
        for key in ('task_id', 'answer_token'):
            message = self.answer(state)
            message[key] = 'invented'
            self.assertEqual(self.send(message)['performance'], 0)

    def test_empty_invalid_answers_do_not_count(self):
        state = self.send({'init': True})
        for value in ([], None, '101,102,103,104'):
            message = self.answer(state)
            message['answer'] = value
            self.assertEqual(self.send(message)['performance'], 0)
        response = self.send(self.answer(state, [True, '102', None, 104]))
        self.assertEqual(response['errors'], 3)

    def test_refresh_keeps_current_task_and_rejects_storage_totals(self):
        state = self.send({'init': True})
        state = self.send(self.answer(state))
        refreshed = self.send({'init': True, 'client_performance': 900})
        self.assertEqual(refreshed['performance'], 1)
        self.assertEqual(refreshed['task_id'], state['task_id'])
        self.assertEqual(refreshed['answer_token'], state['answer_token'])

    def test_another_player_cannot_reuse_attempt(self):
        first = self.send({'init': True})
        message = self.answer(first)
        self.player = Player()
        self.assertEqual(self.send(message)['performance'], 0)

    def test_stop_uses_server_time_and_rejects_later_answers(self):
        state = self.send({'init': True})
        self.now = 1012
        stopped = self.send({'stop_work': True, 'work_seconds': 900})
        self.assertEqual(stopped['work_seconds'], 12)
        self.assertTrue(stopped['stopped_work'])
        self.assertEqual(self.send(self.answer(state))['performance'], 0)
        self.now = 1100
        self.assertEqual(self.send({'stop_work': True})['work_seconds'], 12)

    def test_trial_and_unfinished_binding_ideal_cannot_stop(self):
        self.player.round_number = 1
        self.assertFalse(self.send({'stop_work': True})['stopped_work'])
        self.player.round_number = 2
        self.player.do_ideal = True
        self.player.ideal_to_do = 3
        self.assertFalse(self.send({'stop_work': True})['stopped_work'])

    def test_normal_work_rejects_answer_at_and_after_deadline(self):
        state = self.send({'init': True})
        self.now = 1480
        self.assertEqual(self.send(self.answer(state))['performance'], 0)
        self.now = 1490
        self.assertEqual(self.send(self.answer(state))['performance'], 0)

    def test_binding_work_can_continue_after_deadline_without_more_paid_tasks(self):
        self.player.do_ideal = True
        self.player.ideal_to_do = 2
        state = self.send({'init': True})
        self.now = 1479.9
        state = self.send(self.answer(state))
        self.now = 1480.1
        state = self.send(self.answer(state))
        self.assertEqual((state['performance'], state['performance_in_time']), (2, 1))
        self.assertTrue(state['completed'])
        self.assertTrue(state['stopped_work'])
        self.assertEqual(state['work_seconds'], 480)

    def test_binding_completion_stops_work_before_deadline(self):
        self.player.do_ideal = True
        self.player.ideal_to_do = 1
        state = self.send({'init': True})
        self.now = 1010
        state = self.send(self.answer(state))
        self.assertTrue(state['completed'])
        self.assertEqual(state['work_seconds'], 10)
        self.assertEqual(self.send(self.answer(state))['performance'], 1)

    def test_bonus_protocol_rejects_totals_and_stops_at_five(self):
        state = self.send({'init': True, 'client_performance': 900}, bonus=True)
        self.assertEqual(state['performance'], 0)
        message = self.answer(state)
        state = self.send(message, bonus=True)
        self.assertEqual(self.send(message, bonus=True)['performance'], 1)
        for _ in range(4):
            state = self.send(self.answer(state), bonus=True)
        self.assertTrue(state['completed'])
        self.assertEqual(self.send(self.answer(state), bonus=True)['performance'], 5)

    def test_bonus_has_separate_ids_from_work(self):
        state = self.send({'init': True})
        self.assertEqual(self.send(self.answer(state), bonus=True)['performance'], 0)

    def test_form_fields_do_not_accept_hidden_total_or_time_overwrites(self):
        import ast
        tree = ast.parse((Path(__file__).parents[1] / 'study' / '__init__.py').read_text(encoding='utf-8'))
        for name in ('Task', 'BonusTask'):
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
            assignment = next(n for n in cls.body if isinstance(n, ast.Assign) and
                              any(isinstance(t, ast.Name) and t.id == 'form_fields' for t in n.targets))
            self.assertEqual(ast.literal_eval(assignment.value), [])


if __name__ == '__main__':
    unittest.main()
