import unittest
from types import SimpleNamespace as NS
from sandbox_fast import install, seed_player


def fake_player(config, round_number=1):
    return NS(session=NS(config=config), round_number=round_number,
              participant=NS(vars={}), do_ideal=False, ideal_to_do=999)


class FastModeTests(unittest.TestCase):
    def test_normal_conditions_and_creation_are_preserved(self):
        calls = []
        task = type('Task', (), {})
        survey = type('Survey', (), {'is_displayed': staticmethod(lambda p: p.round_number == 2)})
        ns = dict(creating_session=lambda s: calls.append(s),
                  page_sequence=[task, survey], SandboxResult=type('SandboxResult', (), {}))
        install(ns)
        player = fake_player({}, 1)
        self.assertTrue(task.is_displayed(player))
        self.assertFalse(survey.is_displayed(player))
        player.round_number = 2
        self.assertTrue(survey.is_displayed(player))
        sub = NS(session=player.session)
        ns['creating_session'](sub)
        self.assertEqual(calls, [sub])
        self.assertEqual(player.participant.vars, {})

    def test_only_requested_task_round_is_shown(self):
        task = type('Task', (), {})
        survey = type('Survey', (), {})
        ns = dict(creating_session=lambda s: None, page_sequence=[task, survey],
                  SandboxResult=type('SandboxResult', (), {}))
        install(ns)
        for selected in (2, 6):
            for current in range(1, 7):
                player = fake_player(dict(sandbox_fast_test=True, sandbox_test_round=selected), current)
                self.assertEqual(task.is_displayed(player), current == selected)
                self.assertFalse(survey.is_displayed(player))

    def test_zero_is_a_required_target_not_free_choice(self):
        for target in (None, 0, 5):
            config = dict(sandbox_ideal_target=target, sandbox_test_round=6)
            participant = NS(vars={})
            for current in range(1, 7):
                player = fake_player(config, current)
                player.participant = participant
                seed_player(player)
                self.assertEqual(player.do_ideal, target is not None and current == 6)
                if current == 6:
                    self.assertEqual(player.ideal_to_do, 999 if target is None else target)
            self.assertTrue(participant.vars['sandbox_fast_test'])
            self.assertFalse(participant.vars['consent'])
            self.assertEqual(participant.vars['belief'][0], 100)


if __name__ == '__main__':
    unittest.main()
