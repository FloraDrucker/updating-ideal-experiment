# Two sandbox repairs: checks and limits

29 October 2026. Repository: `ncmnkmp/updating-ideal-experiment-sandbox`.
Branch: `fix/task-counts-and-zero-ideal`. The coauthor's repository and all real
participant data were left unchanged. Nothing was deployed or merged.

## Separate changes

1. `1a9459f`: server-checked answers and single credit per task; safe retries;
   server counts and timing; same protection for bonus tasks.
2. `5d9abc4`: zero ideals start complete, retain zero work/full leisure, survive
   refresh and advance at the original deadline. Unfinished positive ideals can
   still require overtime. Valid immediate stops also retain zero work.

The supporting launcher update uses a new versioned local test directory. It
preserves the previous test databases and avoids loading an old schema.

## Checks completed

- Original ten-participant bot route passed before editing.
- 26 Python server/source checks passed after both repairs. These include
  duplicate/replayed/forged answers, stop and deadline rules, bonus limits,
  zero completion, final saved/export values and existing payment arithmetic in
  both groups. The 480-second zero case saves 0 tasks, 0 work and 480 leisure.
- Eight shared JavaScript client cases passed: repeat clicks, identical-token
  retries, refresh, offline initialization/answers/stops, stale replies and
  enabling fields before restoring keyboard focus.
- Seven actual task callback/timer cases passed in a controlled DOM/clock.
- Full ten-participant consent-to-final-page bot runs passed after each repair.
  Bots submit real answers. They do not simulate elapsed wall-clock work or
  browser interaction; the browser checks below cover those separately.
- Independent source review of each repair found no remaining blocking
  regression. A bonus keyboard-focus regression was found and fixed.

## Actual Chromium and oTree browser checks

All participants and saved values in these checks were synthetic.

- Twenty immediate submission calls credited one correct task. Ten direct
  replays did not add credit. Forged totals of 999999 in init/update/snapshot
  messages, old browser storage and hidden form fields did not change counts.
- Correct and incorrect answer feedback, refresh and deliberately dropped
  acknowledgement recovery passed. The retry credited one task once.
- A real 480-second free-work run advanced and saved 3 accepted tasks, 480 work
  seconds and zero leisure seconds.
- Zero ideal in MAIN and CONTROL, refreshed before the deadline and with the
  browser wall clock changed: both advanced and saved 0 tasks, 0 work seconds
  and 30 leisure seconds in the short fixture.
- A positive ideal completed early survived refresh and retained its work and
  remaining leisure. A five-task ideal finished after the short deadline saved
  five tasks and zero leisure, while its paid count stayed at the one task
  accepted before the deadline.
- Free work stopped normally and ignored forged final form totals. Trial work
  rejected an early Stop and saved the full configured work period.
- Bonus work retained wrong-answer feedback, single credit, automatic keyboard
  focus and five-task completion. The existing option to skip remained available.

The final eight-case browser run passed. An earlier parallel run encountered a
test navigation wait being aborted as pages advanced automatically. Its saved
results were correct; the harness was changed to check the final page state,
and the complete run was repeated successfully.

## What participants may notice

- The count changes after the server confirms an answer. Submit is disabled
  while a reply is pending; retries keep the same attempt.
- Browser-edited totals and clocks no longer determine task credit or work time.
- Server receipt determines whether an answer is within the paid window.
  An answer typed offline but received after the deadline is late.
- Zero ideals lead directly to videos, with no task required. Whole-second
  work-time rounding and the existing payment rates remain unchanged.

Beliefs, ideal/prediction restrictions, treatment allocation, signals, surveys,
payment rates and paid-part selection were not changed.

## Still outside these repairs

- The custom export header defect and the Stata control classification issue.
- A script that computes genuinely correct answers automatically. These repairs
  prevent fabricated totals and repeat credit; they do not prove human work.
- Direct early form submission and other launch/deployment checks in Report 3.
- Production migration, production/network load testing and video availability.
- Multiple independent web workers. Duplicate protection was checked against
  oTree 5.11's serialized, single-worker live requests. A multi-worker deployment
  requires database-level locking or unique accepted-attempt records first.

Use new local sessions for this branch. No historical data were migrated.

## Repeat the local checks

From the sandbox directory:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s sandbox-tests -v
node sandbox-tests/task_client.test.cjs
node sandbox-tests/zero_ideal_page.test.cjs
powershell -NoProfile -ExecutionPolicy Bypass -File .\sandbox.ps1 -Action Bots
```

Approve any transfer to the original experiment separately after reviewing and testing the changes.
