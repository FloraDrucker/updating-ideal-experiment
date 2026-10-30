# Server-checked task counts

Date: 29 October 2026. Scope: sandbox only. First of the two requested repairs.

## Change

The browser submits an answer, a server-issued task ID and a server-issued attempt
token. The server checks the four codes against its stored dictionary and word.
Only a correct answer increases the server's count. Each checked attempt consumes
its token. A retry returns the current state without increasing tasks or mistakes.
Incorrect attempts keep the word and return the same feedback as before.

The browser allows one pending answer. It retains that exact attempt in scoped
session storage and retries it after a lost reply or refresh. Stop requests also
retain their intent until acknowledged. Old browser totals are not restored.

Init, reconnect, hidden form fields and the old deadline-snapshot message cannot
set performance, mistakes or time. Bonus tasks use the same checked protocol,
with a separate task state and the existing five-task completion rule.

The server records time when an answer or stop arrives. Normal work closes at the
configured deadline. Binding-ideal work can still continue afterwards, but only
answers accepted before that deadline count in the paid in-time total. Browser
time is now a display based on server remaining duration and a monotonic clock.
An answer arriving after the deadline is late even if typed earlier offline.

## Regression checks

- `python -m unittest discover -s regression-tests -v`: 15 server protocol cases.
- `node regression-tests/task_client.test.cjs`: 8 client retry/duplicate/focus-order cases.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\sandbox.ps1 -Action Bots`:
  complete ten-participant route in a disposable local database. Bots now submit
  answers rather than claimed totals. They do not fake elapsed work time.
- Actual Chromium/oTree websocket checks passed: 20 submission calls before a
  reply, 10 replays of an accepted attempt, forged totals of 999999 in legacy
  update/init/snapshot messages, a changed hidden total, refresh, incorrect and
  correct answers, and retry after deliberately dropping an acknowledgement.
  Counts remained server-owned, with each accepted task counted once.
- Independent source review found no blocking regression. The bonus keyboard
  focus regression found in review was repaired before this commit.

## Deployment assumptions and limits

oTree 5.11's LiveConsumer serializes live requests with `lock2` and commits inside
that lock. Its supplied production web server uses one worker. The task/token
check and count update therefore run together in the supported single-worker
configuration. Multiple independent web processes require a database-level unique
attempt record or row lock before deployment. This sandbox does not configure a
multi-process deployment.

Two new JSON fields store work and bonus task state. Use a fresh disposable local
database after updating the source. No production database or old participant
record was migrated. Existing source columns are retained.

This prevents duplicate credit and forged totals. It does not prove that a human,
rather than an automated script, computed an otherwise correct answer.

The zero-ideal initial completion flag and zero-work-time finalisation are left
for the second requested repair. Direct early form submission and other report
items are outside this first repair. This is not deployment clearance.
