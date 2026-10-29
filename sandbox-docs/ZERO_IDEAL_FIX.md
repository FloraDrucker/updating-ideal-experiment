# Zero-ideal completion

Date: 29 October 2026. Scope: sandbox only. Second of the two requested repairs.

## Change

A binding ideal of zero is complete when its task page first loads. The server
records zero work and a stopped state immediately; it does not wait for a browser
reply. The browser restores completion from that server state even when the
performance count is zero, shows videos, and advances at the original deadline.
A refresh keeps the same deadline. A refresh after the deadline advances a
completed ideal. Completed ideals also have a remaining-duration server timeout;
unfinished positive ideals retain their existing ability to continue overtime.

Final saving now uses the server's stopped flag, rather than a positive duration,
to distinguish a valid zero from no recorded stop. A zero target therefore saves
zero tasks, zero work seconds and 480 leisure seconds in a normal eight-minute
part, or 30 leisure seconds in the short sandbox fixture. An ordinary immediate
Stop and a positive target completed within the first rounded second also retain
their valid zero duration. Unstopped work and trial rounds still record the full
configured work period. Existing whole-second rounding is retained.

No response restriction, ideal cap, treatment allocation, signal, belief scoring,
survey or payment rate is changed. The existing payment formula now receives the
correct zero-work/full-leisure values. The custom export header defect is outside
this repair; the tests here check that an included zero is retained, not that all
possible export columns are present.

## Verification

- Eleven new Python cases exercise initialization, refresh before/after the
  deadline, valid zero stopping, short/full duration final saves, export values,
  existing payment arithmetic in both treatments, positive overtime and an
  unfinished ideal. Five of the first nine cases failed before the fix.
- Together with the first repair, `python -m unittest discover -s sandbox-tests
  -v` runs 26 server/source checks.
- `node sandbox-tests/zero_ideal_page.test.cjs` executes the actual task callback
  and timer in seven controlled DOM/clock cases: zero, refresh, late refresh,
  positive early and overtime completion, unfinished ideal and immediate Stop.
- `node sandbox-tests/task_client.test.cjs` retains the eight task-client checks
  from the first repair.
- The full ten-participant bot route passed in a fresh disposable database
  (`sandbox.ps1 -Action Bots`, exit 0).
- Actual Chromium/oTree checks passed for zero ideals in MAIN and CONTROL,
  including refresh and a changed browser clock; saved values were 0 tasks,
  0 work seconds and 30 leisure seconds in the short fixture. A positive ideal
  completed before the deadline survived refresh. A positive ideal completed
  after the deadline advanced normally while keeping its pre-deadline paid count.
  Free work, forged final form values, trial timing, bonus completion, bonus
  keyboard focus and bonus skipping also passed.
- An independent source review found no blocking regression.

No live database or real participant record was changed. Use a fresh local test
database for this branch because the preceding task-count fix added model fields.
