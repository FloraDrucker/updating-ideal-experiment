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
