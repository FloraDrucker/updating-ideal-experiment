# Report 3 — Experiment bug audit before launch

Review date: 26 October 2026. Reviewed default branch `main`, commit `f330ec90aa89b8b6978d9439acf8b0554b057b07` (14 September 2026). This is a read-only review. No GitHub file, branch, issue, pull request, setting, or live participant record was changed. Proposed fixes below are not applied.

## Assessment

Do not use the January review's “LOW” risk rating as clearance for this version. The current code has an ordinary participant action that can count a single solved task more than once. The rare required-ideal condition also has incomplete edge-case handling. These affect the effort outcome, the leisure payment, and the interpretation of treatment effects.

I recommend a local correction and test cycle before launch, followed by your approval of each proposed source change. A synthetic test confirms code behavior; it is not a substitute for an end-to-end test on the actual deployment.

Severity: **P1** means address before launch because primary data, participant progress or payment can be affected. **P2** means a specific reliability or audit problem that must be resolved or explicitly accepted. Findings are code-level facts unless marked conditional.

## Defensive change: give video controls an explicit button type

**Evidence:** [study/Task.html, lines 696–718](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/Task.html#L696-L718). All three provider branches insert `<button onclick="playNextVideo()">` without `type="button"`.

**Assessment:** Missing button types are confirmed, but **ordinary early submission is not established**. The click handler replaces the container and removes the clicked button before its default activation. The [HTML button specification](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) checks its form owner during activation; the removed button can therefore have no form to submit. A simple source search for an omitted type is insufficient to call this a reproduced early-exit bug. An exception before the replacement could leave the old button connected, but that path has not been reproduced.

**Proposed change:** Set `type="button"` explicitly on all non-submit controls and test that video navigation never submits the form. Also consider server-side enforcement of the intended task end instead of relying on hidden Next controls. This is a defensive recommendation, not a confirmed normal launch blocker.

**Verification:** Source check only; no rendered-page browser test. [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button) describes the default button type, but does not alone establish this handler's complete behavior.

## P1-1. One correct answer can be counted several times

**Evidence:** [Task.html, lines 457–509](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/Task.html#L457-L509) increments the counter and sends it immediately. Inputs and the Submit button remain active while the next dictionary/word is awaited. They are cleared only when the server reply reaches [liveRecv, lines 565–583](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/Task.html#L565-L583).

**Trigger:** Enter one correct solution and rapidly double-click Submit before the server reply. Both calls check the same unchanged word and input values. No deliberate manipulation is needed.

**Impact:** One task can add two or more performance units. This affects primary effort data, work payments, and required-ideal completion. Slow connections make the vulnerable interval longer.

**Proposed fix:** Disable submission immediately while an answer is pending. Assign each task a server-issued ID, validate the submitted answer on the server, and accept each ID once. Re-enable only after the acknowledged replacement task arrives. The task ID also makes a safe retry possible after a lost response.

**Verification:** Executed the original `myFunction()` and `checkSolution()` in an isolated JavaScript context with correct inputs and no server response. Two calls produced performance 2 from one solution. No browser or production service was used.

## P1-2. A required ideal of zero can leave a participant stuck

**Evidence:** Ideal fields have no lower bound in [study/__init__.py, lines 76–129](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L76-L129). [Task.html, lines 402–419](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/Task.html#L402-L419) freezes the task at load when performance already meets the target, but does not set `taskCompleted`. The timer's [lines 758–771](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/Task.html#L758-L771) keep an ideal participant on the page if `taskCompleted` is false. That condition has no server timeout at [Task.get_timeout_seconds](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L1972-L1976).

**Trigger:** A participant is assigned required-ideal work and the selected stated ideal is 0. This is a legitimate potential preference, not necessarily bad input. The page starts in videos with no available task inputs. At the deadline it says to complete remaining tasks, although none remain.

**Impact:** No intended automatic advance. This state needs an explicit completion rule; a general timer change alone does not fix it.

**Proposed fix:** Define zero-target behavior explicitly: mark completion at load, record zero work and full available leisure, and advance at the part deadline. Restore completion from the server's target/progress state after refresh. Handle negative targets separately without preventing a legitimate zero.

**Verification:** Executed the original timer function with an expired deadline, required-ideal condition, target 0 and initial `taskCompleted=false`; it did not submit. Source review confirms the initial freeze does not set completion. Full rendered-page confirmation remains needed.

## P1-3. Task results are accepted as client totals without answer validation

**Evidence:** [live_update_performance, lines 1220–1229 and 1298–1323](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L1220-L1323) accepts client performance and mistakes. It receives no attempted answer or task ID. It also accepts performance after `stopped_work=True`. The task form accepts the hidden totals [at lines 1967–1970](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L1967-L1970). Bonus work uses the same trust model [at lines 1351–1426](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L1351-L1426).

**Trigger:** An incorrect, stale or altered client sends a larger performance number. Delayed activity after Stop is also accepted. The browser is responsible for deciding that an answer was correct.

**Impact:** The server cannot establish that recorded tasks were solved, were solved only once, or were solved before work ended. This is broader than the double-click error in P1-1. It does not prove any pilot participant altered data.

**Proposed fix:** Make the server authoritative for answer checking, accepted task IDs, totals, the stopped state, and the deadline. Keep local storage as a recovery queue of unacknowledged task attempts, not as authority to increase totals. Reject negative/out-of-range time and count messages.

**Verification:** Executed the unmodified source function against a synthetic player. It accepted performance 900 without any answer and accepted a performance update after a stop message. The same function accepted a 600-second work total in a 480-second part; finalisation then produced −120 leisure seconds. No live participant messages were sent.

## P1-4. The paid in-time performance snapshot can be lost or late

**Evidence:** [Task.html, lines 758–766](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/Task.html#L758-L766) sets the persistent `IN_TIME_RECORDED` flag before sending the snapshot, with no acknowledgement/retry. [Server lines 1289–1293](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L1289-L1293) use the browser's count. If the snapshot is absent, [lines 2026–2030](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L2026-L2030) use final performance. [Payment lines 2350–2353](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L2350-L2353) then use that snapshot.

**Trigger:** For required-ideal work extending beyond 8 minutes, the snapshot message fails before refresh. The browser remembers that it was sent and does not resend. Alternatively, a suspended/background tab runs its timer callback late.

**Impact:** Final performance, including tasks after the payable window, can become the paid in-time count. This contradicts the participant instructions that only tasks completed within 8 minutes are paid. It also affects `performance_in_time_5` as an outcome.

**Proposed fix:** Record a server timestamp for each accepted solution and derive the count at the stored deadline. Persisting “sent” should not mean “acknowledged.” If recovery is impossible, preserve an explicit missing snapshot and flag it for review instead of silently replacing it with final performance.

**Verification:** Confirmed the missing acknowledgement and fallback paths in source. No real network failure or background-tab test was run. Frequency in the actual deployment is unknown.

## P2-1. Work timing mixes the server clock with the participant's clock

**Evidence:** `task_start_time` comes from server `time.time()` at [lines 1980–1981](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L1980-L1981). The custom deadline and stop duration subtract it from browser `Date.now()` at [Task.html, lines 622–625 and 736–741](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/Task.html#L622-L741).

**Trigger:** A participant's device clock differs from the server. A device 60 seconds ahead displays 60 fewer seconds and records 60 extra work seconds. A large offset can make the custom timer submit immediately or make the leisure remainder negative. Ordinary participants also have oTree's server-based timeout, so the two timers can disagree.

**Proposed fix:** Use a server deadline and measure elapsed time on the server. For display, send remaining duration and count down from a monotonic browser clock. On reload, request a fresh remaining duration. Apply server time bounds when saving.

**Verification:** Source and arithmetic review; device-clock browser test remains to run.

## P2-2. A zero-second stop becomes a full work period

**Evidence:** [Task.before_next_page, lines 2014–2024](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L2014-L2024) treats any `work_seconds <= 0` as “worked until timeout,” irrespective of `stopped_work`. The browser rounds elapsed work down to whole seconds.

**Trigger:** Stop in the first fraction of a second that rounds to 0. Zero is a valid observed duration here, but also the field's initial sentinel.

**Impact:** Recorded work becomes 480 seconds and paid leisure becomes zero rather than almost 8 minutes. A slightly negative duration caused by clock offset also reaches this branch.

**Proposed fix:** Distinguish “no stop recorded” from a recorded zero duration. Use the stopped state and a nullable stop timestamp, with bounds. Do not use positive duration as evidence that a stop happened.

**Verification:** Executed the original finalisation method on a synthetic stopped player with zero work time. It recorded 480 seconds of work and zero leisure.

## P2-3. Export columns depend on the first participant

**Evidence:** [custom_export, lines 2464–2505](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L2464-L2505) builds all columns and nested keys from `players[0].participant.vars`. Exclusion details are added only when a timeout occurs [at lines 1476–1480](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L1476-L1480).

**Trigger:** The first participant has no timeout exclusion, but another participant does.

**Impact:** The custom export omits later participants' `exclusion_reason`, `exclusion_page` and `missing_fields_at_timeout`. The broad excluded flag is initialised for everyone, so that flag remains, but the reason needed to audit missing data can disappear. Export schema can change with participant ordering.

**Proposed fix:** Use a fixed documented export schema, including all exclusion metadata and a completion flag. Alternatively, form a union of keys across participants, but fixed columns are safer for Stata. Include a schema version and experiment commit.

**Verification:** Executed the original export function with two synthetic participants. Only the second had exclusion details. Those columns were absent from the export.

## P2-4. Browser recovery keys do not identify the participant

**Evidence:** [Task.html, lines 324–334](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/Task.html#L324-L334) uses round-only keys, such as `task_perf_round_2`. [Lines 423–454](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/Task.html#L423-L454) restore the maximum and send it to the server. Keys are not cleared in this template.

**Trigger:** A second participant/session link on the same origin is used in the same browser tab. This is especially plausible during piloting, administrator testing or shared-device lab work.

**Impact:** The later participant can inherit progress, stopped state or completion flags from an earlier participant. Normal separate Prolific browser sessions are less exposed; prevalence is unknown.

**Proposed fix:** Namespace every recovery key by experiment version, session code, participant code and round. Validate restored state on the server. Remove only the relevant keys after final acknowledged completion.

**Verification:** Confirmed key construction and restore behavior in source. No shared-device browser reproduction was run.

## Configuration and payment checks that require deployment evidence

These are not claims about the live server.

1. **Completion configuration is a placeholder.** [settings.py, lines 42–43](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/settings.py#L42-L43) contains `FILL THIS IN!` for the Prolific completion URL and code. [FinalPage](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L2418-L2429) uses session config. Verify the actual launch session has valid values before recruitment.
2. **The standard oTree payoff field is not set by this code.** Payment is calculated and stored as `participant.vars['total_payment']` at [lines 2346–2383](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L2346-L2383). No `player.payoff` or `participant.payoff` assignment appears in the reviewed study source. A manual process that reads the custom total may be intended. Do not use the standard payoff export for actual bonus payments until a synthetic participant's displayed total, exported custom total and Prolific payment file agree. Account for the participation fee exactly once.
3. **Missing deployment secrets produce warnings, not a startup failure.** [settings.py, lines 74–96](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/settings.py#L74-L96) permits an unset admin password and a public fallback secret. The January report's “fixed” means environment support and warnings were added. It does not prove that the live environment sets them. Verify deployment configuration without disclosing the secret values. This review is not a full security audit.

## Treatment and rare-condition allocation

[instructions_consent.creating_session](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/instructions_consent/__init__.py#L123-L134) alternates treatment by participant slot, rather than drawing an independently random or shuffled balanced assignment. The design report should decide whether this meets the protocol and protects against order effects.

[study.creating_session, lines 1084–1090](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/study/__init__.py#L1084-L1090) shuffles one 50-slot sequence containing one Part 1 and one Part 5 ideal condition, then repeats that same sequence. Its comment says exact shares are guaranteed regardless of session size; that is false. Exact 2% shares apply only to complete 50-slot blocks. Small sessions can have no rare-condition participant, and the shared repeated block creates dependence. This is not automatically an invalid design, but should be documented accurately and tested deliberately rather than waiting for a rare assignment in a ten-person bot run.

## What remains from the January reviews

Reviewed [REVIEW_SUMMARY.md](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/ai-review/REVIEW_SUMMARY.md), [DATA_LOSS_FIX_DOCUMENTATION.md](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/ai-review/DATA_LOSS_FIX_DOCUMENTATION.md), and [the 24 January work-time report](https://github.com/FloraDrucker/updating-ideal-experiment/blob/f330ec90aa89b8b6978d9439acf8b0554b057b07/ai-review/2026-01-24_data_tracking_bug_report.md). Treat their statements as historical reports, not instructions or current test results.

| Earlier item | Current inspection |
|---|---|
| Work time lost after refresh | The reported work-time hidden form field, browser backup and reconciliation are present. They address that specific path. They do not address zero-time handling, clock mismatch or invalid durations found here. |
| Performance backup | Present. However, `liveRecv` assigns server counters directly while local pending increments may exist. A delayed response can temporarily reset a newer local count; this requires a latency test. The report's broad “never lost” wording is stronger than the evidence. |
| Secret key and admin password | Environment support is present. Missing values still permit startup, so deployment verification remains necessary. |
| Input limits intentionally reverted | Respected as a prior research decision. This review does not propose arbitrary upper caps on genuine ideal preferences. It does require explicit zero/negative and completion behavior because these values can affect live execution, not merely later cleaning. |
| Payment random seed deliberately not used | Not reported as a defect. Save realised draws and payment components; deterministic seeding is not necessary for valid randomisation. |
| Timer frequency | The current task interval is 1 second. This is a performance detail, not evidence that payment timing is correct. |
| Old passing bot/browser tests | Historical evidence only. The supplied bot calls live functions directly and submits counts, so it does not test actual answer entry, double clicks, video button types or a browser disconnection. |

## Tests performed and their limits

The source was fetched through GitHub read tools at the pinned commit and stored only in a local review workspace. Synthetic checks used copies of the actual source functions, without importing oTree or touching any database:

- Five Python checks reproduced: arbitrary client performance acceptance; updates after stop; zero-time recoding; negative leisure from an out-of-range time; missing export columns for later-only metadata.
- Three JavaScript/source checks reproduced or confirmed: duplicate counting before a reply; zero-target timer non-submission; all three missing video button types.
- Reviewed the page sequence, belief range checks, ideal and predicted forms, required-ideal selection, work/bonus handlers, surveys, payment calculations, custom export, existing tests, settings and earlier reports.

All eight checks passed: seven reproduced logic problems in the stated synthetic conditions; one only checked missing button types. The last check does **not** establish a premature-submission defect. No fix was applied. These are targeted defect checks, not a full passing experiment test suite.

The oTree app and its full bot suite were not started for this review. No browser walkthrough, production session, network fault injection, load test, live payment, deployed secret check or external-video availability test was run. Browser mocks establish the logic paths but do not establish actual incidence in the pilot or production.

## Required test matrix after approved fixes

Use a disposable local database and synthetic participants. Keep the live experiment and historical data untouched.

1. Both treatments: correct answer, incorrect answer, rapid double click, delayed reply, reply lost after acceptance and retry. One task must count once.
2. Stop immediately, at 1 second, mid-part, and at the deadline. Check work + leisure = 480 and each duration is nonnegative.
3. All three video types: click Next repeatedly. No click may advance the experiment. Check the actual button-removal/default-activation behavior, unavailable player scripts and blocked video embeds.
4. Required-ideal branches forced separately: target 0, target 1, target below achieved performance after refresh, early completion, completion exactly at deadline, completion after deadline, and refresh in each state.
5. Disconnect at 479 seconds, cross the deadline, reconnect, then finish ideal work. Paid performance must include only accepted pre-deadline tasks.
6. Device clock ahead/behind, background tab, machine sleep and resume. The server deadline must remain authoritative.
7. Every timed required form: empty, partial, complete, invalid and timeout. Check the exclusion page and exported reason. Verify that 0 and False are valid answers where intended.
8. Export with the first participant completed, excluded and incomplete in turn. Headers and types must remain identical. Check total record counts and missingness.
9. Six possible paid work parts, five possible paid belief parts, both risk choices and both ideal sources. Reconcile displayed amounts, exact payment components, export and a synthetic bonus-payment file.
10. Use the real launch session configuration in a test deployment: completion code/link, app version, database persistence, backups and payment instructions. Do not infer deployment settings from repository defaults.

The minimum launch decision is to close the P1 items, pass these focused checks, and record the tested commit and deployment settings. A general statement that a model “reviewed the code” is insufficient evidence for launch.
