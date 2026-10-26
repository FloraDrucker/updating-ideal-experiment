"""Opt-in local fixtures and page shortcuts; never repair the tested task logic."""


def seed_player(player):
    config = player.session.config
    target = config['sandbox_ideal_target']
    pp = player.participant.vars
    if player.round_number == 1:
        pp.update(
            sandbox_fast_test=True, treatment=config.get('sandbox_treatment', True), consent=False,
            consent_no_ai=False, excluded=False, total_wrong=None,
            success_attempt=None, attempt_number=0,
            wrong_questions_attempt1='', wrong_questions_attempt2='',
            do_ideal=target is not None, ideal_index=12 if target is not None else None,
            ideal_to_do=target if target is not None else 999,
        )
        # Explicit synthetic fixtures replace information from skipped pages.
        pp['belief'] = {i: 100 for i in (0, 2, 3, 4, 5)}
        pp['ideal'] = {i: 10 for i in range(1, 13)}
        pp['predicted'] = {i: 8 for i in range(1, 13)}
        pp['risk_choices'] = {i: 0 for i in range(21)}
        pp['actual'] = {i: 0 for i in range(6)}
        pp['mistakes'] = {i: 0 for i in range(6)}
        pp['work_seconds'] = {i: 0 for i in range(6)}
        pp['nonwork_seconds'] = {i: 0 for i in range(6)}
        if target is not None:
            pp['ideal'][12] = target
            pp['predicted'][12] = min(8, target)
    player.do_ideal = target is not None and player.round_number == config['sandbox_test_round']
    player.ideal_to_do = target if player.do_ideal else 999
    if player.do_ideal:
        player.ideal_index = 12


def install(namespace):
    """Only shortcut flagged sessions. Preserve normal page conditions and hooks."""
    original_creation = namespace['creating_session']

    def creating_session(subsession):
        original_creation(subsession)
        if subsession.session.config.get('sandbox_fast_test', False):
            for player in subsession.get_players():
                seed_player(player)

    namespace['creating_session'] = creating_session
    for page in namespace['page_sequence']:
        original_display = getattr(page, 'is_displayed', None)

        def is_displayed(player, page_name=page.__name__, original=original_display):
            config = player.session.config
            if config.get('sandbox_fast_test', False):
                pages = config.get('sandbox_pages', ['Task'])
                return page_name in pages and player.round_number == config['sandbox_test_round']
            return original(player) if original is not None else True

        page.is_displayed = staticmethod(is_displayed)
    namespace['page_sequence'].append(namespace['SandboxResult'])
