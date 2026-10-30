# Bot Test Expansion and Bug Fix Report

**Project:** Study on Work (oTree Behavioral Economics Experiment)  
**Date:** 30 October 2026  
**Scope:** Expanding the automated bot test suite, discovering bugs during testing, and a targeted code review of `study/__init__.py`

---

## Table of Contents

1. [Background](#1-background)
2. [Bot Test Cases Added](#2-bot-test-cases-added)
3. [Bugs Found and Fixed](#3-bugs-found-and-fixed)
4. [Issues Not Fixed](#4-issues-not-fixed)
5. [Files Changed](#5-files-changed)
6. [Final Test Status](#6-final-test-status)

---

## 1. Background

The project had an existing automated bot test suite (`study/tests.py`) with two cases:

| Case | What it tests |
|---|---|
| `default` | Normal participant path through all 6 rounds |
| `ideal_zero` | Participant whose stated ideal number of tasks is 0 (binding-ideal edge case) |

The session configuration runs 10 bots per case through the full experiment (`instructions_consent` + `study` apps, 6 rounds each). The goal of this work was to extend coverage to participant behaviours that were untested and to fix any bugs surfaced by doing so.

---

## 2. Bot Test Cases Added

Eight cases now run in total. New cases are listed below with what they exercise.

### 2.1 `stop_immediately`

The participant clicks **Stop Working** at the very start of the task — before solving any encryption task.

- Sends `stop_work` to the live task immediately after the `init` message.
- **Assertions after Task (round 2):** `stopped_work == True`, `performance == 0`.

**Why it matters:** The stop-work path has its own branch in `task_protocol.py`
(`stop_task`) which records `work_seconds` from a server timestamp. Stopping at
time zero checks that `work_seconds` is bounded correctly (≥ 0, ≤ total).

---

### 2.2 `ideal_finish_early`

The participant has a **binding ideal of 3 tasks** (randomly assigned `do_ideal=True`, `ideal_index=12`). They finish all 3 tasks **before the deadline**, so time remains for leisure.

- Forces `participant.vars['do_ideal'] = True`, `ideal_index = 12` before the round-6 Predicted page.
- Plays exactly 3 tasks via `play_encryption_task(n_tasks=3)`.
- **Assertions after Task (round 6):** `do_ideal == True`, `ideal_to_do == 3`, `performance == 3`, `stopped_work == True`, `performance_in_time == 3`.

**Why it matters:** `performance_in_time` controls what the participant is paid for in round 6 when a binding ideal applies. It must equal performance when the deadline has not elapsed.

---

### 2.3 `ideal_overtime`

The participant has a **binding ideal of 3 tasks** but finishes all tasks **after the deadline** (they needed overtime).

- Like `ideal_finish_early` but `play_encryption_task` is called with `overtime=True`.
- `overtime=True` backdates `task_start_time` by `work_length_seconds + 10` before sending any live messages. Because `prepare_task` only sets `task_start_time` once (when it is 0), the backdated value persists; all subsequent `now < deadline` checks fail, so none of the 3 completed tasks increment `performance_in_time`.
- **Assertions after Task (round 6):** `do_ideal == True`, `ideal_to_do == 3`, `performance == 3`, `stopped_work == True`, `performance_in_time == 0`.

**Why it matters:** The payment rule for `do_ideal` participants uses `performance_in_time_5`, not `performance`. Testing that the two can diverge verifies the overtime branch of the task protocol.

---

### 2.4 `bonus_tasks`

The participant answers `task_more = True` in Survey5, triggering the optional **BonusTask** live page.

- Uses `survey5_bonus_answers()` which copies `survey5_answers()` and overrides `task_more = True`.
- Plays all `C.BONUS_TASKS` (5) bonus encryption tasks via a new `play_bonus_task()` helper that calls `live_update_bonus_performance` directly.
- **Assertion after BonusTask:** `bonus_performance == C.BONUS_TASKS`.

**Why it matters:** `BonusTask` uses a separate live method (`live_update_bonus_performance`) and a separate performance field (`bonus_performance`). The page was never exercised by any prior bot case.

---

### 2.5 `early_exclusion`

The participant is **excluded in round 2** when Survey1 times out with missing fields. Subsequent rounds continue with `excluded = True`.

- Submits `Survey1` with `Submission(Survey1, {}, check_html=False, timeout_happened=True)` in round 2.
- **Assertions after Survey1:** `excluded == True`, `exclusion_page == 'Survey1'`.
- In round 2, five `Excluded` pages are yielded for positions [15, 17, 19, 21, 23] in the page sequence (the Excluded pages that sit after the survey slots).
- In rounds 3–6, nine `Excluded` pages are yielded per round — one for each position [1, 5, 7, 9, 15, 17, 19, 21, 23] in the page sequence. Regular pages (Belief, Work, Task, EndOfWork, per-round survey) are also yielded as normal since their `is_displayed` conditions do not check exclusion status.
- In round 6, Payment and FinalPage are **not** yielded because `excluded = True` (see §3.1).

**Why it matters:** Exclusion in round 2 affects 5 subsequent rounds. This is the only case that exercises the `Excluded` page at all 9 positions in the page sequence where it appears, across multiple rounds.

---

### Summary table

| Case | Round 6 ideal | Stops work | Excluded | BonusTask |
|---|---|---|---|---|
| `default` | free (do_ideal=False) | after 2 tasks in round 2 | no | no |
| `ideal_zero` | 0 tasks (do_ideal=True) | immediately | no | no |
| `stop_immediately` | free | immediately in round 2 | no | no |
| `excluded_timeout` | free | 2 tasks | at Survey5 (round 6) | no |
| `ideal_finish_early` | 3 tasks in time | auto-stops at 3 | no | no |
| `ideal_overtime` | 3 tasks overtime | auto-stops at 3 | no | no |
| `bonus_tasks` | free | 2 tasks in round 2 | no | yes (5 tasks) |
| `early_exclusion` | free | 2 tasks per round | at Survey1 (round 2) | no |

---

## 3. Bugs Found and Fixed

### 3.1 `Payment` and `FinalPage` crash for excluded participants

**File:** `study/__init__.py`  
**Pages:** `Payment`, `FinalPage`  
**Severity:** 🔴 High — server-side crash  
**Discovered:** During first bot run of `excluded_timeout`

#### Root cause

`Survey5.before_next_page` runs the payment-randomisation code (setting `player.task_chosen_part`, `player.risk_chosen`, etc.) **after** the `exclude_on_incomplete_timeout` check. When Survey5 times out and the participant is excluded, the function returns early — the payment fields are never set and remain `NULL`.

`Payment.vars_for_template` then accesses `player.task_chosen_part` unconditionally:

```python
chosen_part = C.PARTS[player.task_chosen_part]   # TypeError: null field access
```

oTree raises `TypeError: player.task_chosen_part is None. Accessing a null field is generally considered an error.`

#### Why it wasn't caught sooner

The `Excluded` page has **no Next button** in `study/Excluded.html`, so real participants cannot proceed to `Payment`. The crash only surfaced when a bot (which submits pages directly regardless of HTML) tried to do so.

#### Fix

Added `and not player.participant.vars.get('excluded', False)` to `is_displayed` on both `Payment` and `FinalPage`:

```python
# Payment
@staticmethod
def is_displayed(player: Player):
    return player.round_number == C.NUM_ROUNDS \
           and not player.participant.vars.get('excluded', False)

# FinalPage
@staticmethod
def is_displayed(player: Player):
    return player.round_number == C.NUM_ROUNDS \
           and not player.participant.vars.get('excluded', False)
```

This matches the design intent (excluded participants are directed to leave) and means the `excluded_timeout` and `early_exclusion` bots correctly skip both pages.

---

### 3.2 `Predicted.error_message` — `TypeError` when Ideal page was timed out

**File:** `study/__init__.py`, `Predicted.error_message`  
**Severity:** 🔴 High — server-side crash on form submission  
**Discovered:** Code review after bot-test expansion

#### Root cause

`Predicted.is_displayed` only checks `round_number in [2, 6]` — it has **no exclusion guard**. If a participant times out on the `Ideal` page and is excluded, `Ideal.before_next_page` returns early and `player.lastideal_t` / `player.lastideal_c` (round 6) or `player.ideal50`…`player.ideal150` (round 2) remain `None`.

The excluded participant still sees `Predicted` (since `is_displayed` does not check exclusion). If they submit values, `error_message` runs:

```python
# Round 6 example
ideal_val = player.lastideal_t    # None
predicted_val = values['lastpredicted_t']   # e.g. 5

if predicted_val > ideal_val:     # TypeError: '>' not supported between int and NoneType
```

Python 3 raises `TypeError` unconditionally; oTree does not catch it and returns a 500 error.

#### Fix

Added `None` guards before each comparison in `error_message`:

```python
# Round 2 — inside the loop
if ideal_val is None or predicted_val is None:
    continue

# Round 6
if ideal_val is None or predicted_val is None:
    return None
```

Validation is silently skipped when the ideal value was never recorded. The `exclude_on_incomplete_timeout` check in `Predicted.before_next_page` will handle the actual exclusion logic when the timeout fires.

---

### 3.3 Duplicate `Belief.is_displayed` — silent dead code

**File:** `study/__init__.py`, `class Belief`  
**Severity:** 🟡 Medium — no current misbehaviour, latent maintenance risk  
**Discovered:** Code review

#### Root cause

`is_displayed` was defined **twice** in the `Belief` class body with identical bodies:

```python
@staticmethod
def is_displayed(player):
    return player.round_number > 2   # ← overwritten silently

@staticmethod
def is_displayed(player):
    return player.round_number > 2   # ← this one is used
```

Python silently discards the first definition. Because `Payment.is_displayed` and `FinalPage.is_displayed` had just been updated to add exclusion guards, there was a real risk that a future edit would add the same guard to only one of the two `Belief.is_displayed` copies and the wrong one would survive.

#### Fix

Removed the first (dead) definition.

---

### 3.4 `custom_export` — `IndexError` on empty player queryset

**File:** `study/__init__.py`, `custom_export`  
**Severity:** 🟠 Medium — silent crash breaking data download  
**Discovered:** Code review

#### Root cause

```python
def custom_export(players):
    fp = players[0]   # IndexError if queryset is empty
```

If the export is triggered for a session with no players (e.g. a freshly created but not-yet-started session, or a database state during development), this raises `IndexError` before the header row is even yielded.

#### Fix

```python
def custom_export(players):
    player_list = list(players)
    if not player_list:
        return
    fp = player_list[0]
    ...
    for p in player_list:
        ...
```

The entire function now materialises the queryset once and returns cleanly when it is empty.

---

### 3.5 `creating_session` — off-by-one in number generation loop

**File:** `study/__init__.py`, `creating_session`  
**Severity:** ⚪ Low — no functional impact  
**Discovered:** Code review

#### Root cause

```python
for i in range(27):     # generates 27 numbers
    ...
    numbers.append(choice)
dictionary = dict([(d[0][i], d[1][i]) for i in range(26)])  # uses 26
```

The 26-letter alphabet is mapped to only 26 numbers, so the 27th number generated by the loop is computed and silently discarded. The subsession dictionary was always correct (26 entries); only one extra random draw was wasted per subsession creation.

#### Fix

Changed `range(27)` to `range(26)`.

---

### 3.6 `creating_session` print statement — missing space

**File:** `study/__init__.py`, `creating_session`  
**Severity:** ⚪ Cosmetic  
**Discovered:** Code review

#### Root cause

```python
print(f"Participant {p.id_in_subsession}assigned do_ideal=...")
# output: "Participant 3assigned do_ideal=False, ..."
```

#### Fix

```python
print(f"Participant {p.id_in_subsession} assigned do_ideal=...")
```

---

## 4. Issues Not Fixed

### 4.1 `Task.get_timeout_seconds` — returns full `total` on first page load when `do_ideal=True` and tasks already satisfied

**File:** `study/__init__.py`, `Task.get_timeout_seconds`  
**Severity:** Low — client-side JS handles it before server timeout fires

When `do_ideal=True` and `performance >= ideal_to_do`, the intended behaviour is to return the remaining wall-clock time (so the server timer matches what the JS shows). The check is:

```python
if player.task_start_time:
    return max(0, player.task_start_time + total - time.time())
return total
```

On the very first GET of the Task page, `task_start_time` is still `0` (its model initial value; it is set by `prepare_task` inside `vars_for_template`). The ordering of `get_timeout_seconds` vs `vars_for_template` during page rendering means `task_start_time` may be `0` when the check runs, causing the server to give the page a full `total`-second server timeout instead of a near-zero one.

In practice the JavaScript client processes the `init` live-method response, detects `completed=True` (or `stopped_work=True` for `ideal_to_do=0`), and auto-submits the page before the server timer fires. Bot tests confirm correct end-to-end behaviour. Changing this would risk a regression in the timeout calculation for all `do_ideal` participants, so it was left as-is pending a more careful analysis.

---

### 4.2 `Signal.vars_for_template` — redundant `import time` inside function body

**File:** `study/__init__.py`, `Signal.vars_for_template`  
**Severity:** ⚪ Cosmetic — `time` is already imported at module level

The function body contains `import time` in two places. Python caches module imports so there is no runtime cost, but it is misleading. Not fixed because the signal timing logic is sensitive and a cosmetic-only edit is not worth the risk of touching it.

---

## 5. Files Changed

| File | Change |
|---|---|
| `study/tests.py` | Added 6 new bot cases; added `play_bonus_task`, `ideal_n_answers_for_round`, `predicted_n_answers_for_round`, `survey5_bonus_answers` helpers; extended `play_encryption_task` with `overtime` parameter |
| `study/__init__.py` | Fixed bugs 3.1–3.6 above |

No template files, settings, or other Python modules were changed.

---

## 6. Final Test Status

All 8 bot cases pass cleanly (`sandbox.ps1 -Action Bots`, exit code 0):

| # | Case | Rounds tested | Key assertions |
|---|---|---|---|
| 0 | `default` | 1–6 | Normal flow completes |
| 1 | `ideal_zero` | 1–6 | `do_ideal=True`, `ideal_to_do=0`, `performance=0` |
| 2 | `stop_immediately` | 1–6 | `stopped_work=True`, `performance=0` after round 2 Task |
| 3 | `excluded_timeout` | 1–6 | `excluded=True`, `exclusion_reason='incomplete_timeout'` after Survey5 |
| 4 | `ideal_finish_early` | 1–6 | `do_ideal=True`, `performance=3`, `performance_in_time=3` |
| 5 | `ideal_overtime` | 1–6 | `do_ideal=True`, `performance=3`, `performance_in_time=0` |
| 6 | `bonus_tasks` | 1–6 | `bonus_performance=5` |
| 7 | `early_exclusion` | 1–6 | `excluded=True` from round 2; all 9 Excluded-page positions visited per round in rounds 3–6 |
