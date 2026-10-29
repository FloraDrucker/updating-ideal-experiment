"""Server-owned task attempts. The oTree live request lock covers check and save."""
import json
import time
import uuid


def _field(bonus):
    return 'bonus_task_protocol' if bonus else 'task_protocol'


def _new_task(state, build_dict, build_word, task_length):
    state.update(task_id=uuid.uuid4().hex, answer_token=uuid.uuid4().hex,
                 encryption_dict=build_dict(), word_list=build_word(task_length))


def _save(player, state, bonus):
    setattr(player, _field(bonus), json.dumps(state))
    # Preserve the existing inspection/export fields; task_protocol is authoritative.
    player.current_dict = json.dumps(state['encryption_dict'])
    player.current_word = json.dumps(state['word_list'])


def task_state(player, bonus, build_dict, build_word, task_length):
    encoded = player.field_maybe_none(_field(bonus))
    if encoded:
        return json.loads(encoded)
    state = {'revision': 0}
    _new_task(state, build_dict, build_word, task_length)
    _save(player, state, bonus)
    return state


def _elapsed(player, now):
    total = player.session.config['work_length_seconds']
    return min(total, max(0, int(now - player.task_start_time)))


def stop_task(player, now):
    if not player.stopped_work:
        player.work_seconds = _elapsed(player, now)
        player.stopped_work = True


def prepare_task(player, now):
    """Restore server completion without resetting the part's original clock."""
    if player.task_start_time == 0:
        player.task_start_time = now
    if player.do_ideal and player.performance >= player.ideal_to_do:
        if player.ideal_to_do == 0:
            # No work was required, even if the first live reply arrives late.
            player.work_seconds = 0
            player.stopped_work = True
        elif not player.stopped_work:
            stop_task(player, now)


def handle_task_message(player, data, *, bonus, task_length, bonus_tasks,
                        build_dict, build_word):
    """Accept an answer/token, never a claimed total, duration or paid snapshot.

    oTree 5.11 runs each live handler inside lock2 and a committed session scope.
    Its supported server uses one web worker. Do not run independent web workers
    against this protocol without database row locking or a unique-attempt table.
    """
    now = time.time()
    if not bonus:
        prepare_task(player, now)
    state = task_state(player, bonus, build_dict, build_word, task_length)
    perf_field = 'bonus_performance' if bonus else 'performance'
    mistake_field = 'bonus_mistakes' if bonus else 'mistakes'
    if not bonus and player.field_maybe_none('performance_in_time') is None:
        player.performance_in_time = 0
    total = player.session.config['work_length_seconds']
    deadline = player.task_start_time + total
    completed = lambda: (getattr(player, perf_field) >= bonus_tasks if bonus else
                         player.do_ideal and player.performance >= player.ideal_to_do)
    response = {}
    if not isinstance(data, dict):
        data = {}
    if data.get('stop_work') and not bonus:
        # Trial cannot stop; a binding ideal must be completed first.
        if player.round_number > 1 and (not player.do_ideal or completed()):
            stop_task(player, now)
            state['revision'] += 1
        else:
            response['rejected'] = 'work_required'
    elif 'answer' in data:
        response['reply_to'] = data.get('answer_token')
        closed = completed() or (not bonus and (
            player.stopped_work or (not player.do_ideal and now >= deadline)))
        if (data.get('task_id') != state['task_id'] or
                data.get('answer_token') != state['answer_token']):
            # Includes retries after a lost acknowledgement. Return current state.
            response['rejected'] = 'stale_attempt'
        elif closed:
            response['rejected'] = 'work_finished'
        else:
            answer = data['answer']
            if not isinstance(answer, list) or len(answer) != task_length:
                response['rejected'] = 'invalid_answer'
            else:
                expected = [state['encryption_dict'][letter] for letter in state['word_list']]
                errors = sum(type(value) not in (int, float) or value != expected[i]
                             for i, value in enumerate(answer))
                response.update(accepted=errors == 0, errors=errors)
                state['revision'] += 1
                # Rotate on incorrect attempts too, so retry cannot count another mistake.
                state['answer_token'] = uuid.uuid4().hex
                if errors:
                    setattr(player, mistake_field, getattr(player, mistake_field) + 1)
                else:
                    setattr(player, perf_field, getattr(player, perf_field) + 1)
                    if not bonus:
                        if now < deadline:
                            player.performance_in_time += 1
                        if completed():
                            stop_task(player, now)
                    _new_task(state, build_dict, build_word, task_length)
    # init/request_update/record_in_time/legacy total messages only return server state.
    _save(player, state, bonus)
    response.update(
        init=bool(data.get('init')), revision=state['revision'],
        task_id=state['task_id'], answer_token=state['answer_token'],
        performance=getattr(player, perf_field), mistakes=getattr(player, mistake_field),
        encryption_dict=state['encryption_dict'], word_list=state['word_list'],
        completed=bool(completed()), shuffle=False,
    )
    if not bonus:
        response.update(work_seconds=player.work_seconds,
                        stopped_work=player.stopped_work,
                        remaining_seconds=max(0, deadline - now),
                        performance_in_time=player.performance_in_time)
    return {player.id_in_group: response}
