# Direct-access mode validation

26 October 2026. Local branch: `sandbox/fast-bug-checks`.

- Three focused unit tests passed: normal page conditions and creation remain intact; only the selected task round is displayed; zero is a compulsory target rather than free choice.
- Python compilation passed.
- The supplied normal 10-participant bot test passed with shortcut mode disabled.
- Browser check: the 30-second demo's P1 link opened directly at round 2 Task without consent, comprehension, trial or surveys.
- Browser check: Stop working followed by the deadline opened the result page. It displayed 19 work seconds and 11 leisure seconds, total 30.
- Browser check: the zero-ideal demo opened directly at round 6 Task with 0 out of 0 tasks and the task inputs hidden. After the deadline it remained on Task and displayed "Time is up — please complete your remaining tasks." The original zero-target defect is therefore still visible.
- `study/Task.html`, `live_update_performance`, `Task.before_next_page` and the original payment code were not changed. Synthetic setup and page display rules are opt-in under `SANDBOX_FAST_TEST=1`; normal Start clears that process flag.

No bug correction, GitHub push, original-repository change or production deployment was performed. The manual zero-stop console test and full rare-condition/network-failure matrix remain separate tests. Short sessions change the configured duration, so their expected work-plus-leisure total is 30 rather than 480.

## Form shortcuts extension

- Four focused unit tests pass, including selection of only the configured form pages and correct MAIN/CONTROL fixture assignment.
- Browser: MAIN Part 5 opens directly at Belief, advances to Ideal and Predicted, rejects prediction 13 after ideal 12, then accepts prediction 10 and shows the saved belief 110 / ideal 12 / prediction 10.
- Browser: CONTROL Part 1 opens directly at the original ideal table with the 120-point column highlighted. Entering the anchor unlocks the other fields. Submitting eleven ideals and predictions reaches a readable saved-answer summary with the correct 50–150 benefit labels.
- Original belief/ideal/prediction templates and validation methods were not edited. These routes only change page selection and synthetic prerequisites in opt-in local sessions.
- All five questionnaire shortcuts are configured. Full manual completion of every questionnaire, both treatment variants of every route, and every timeout branch remain untested.
