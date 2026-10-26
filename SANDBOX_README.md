# Private experiment sandbox

This is an independent test copy owned by ncmnkmp. Do not recruit real participants or make real payments here. The original FloraDrucker repository is unchanged.

## What was copied

The main branch and its reachable history were copied from https://github.com/FloraDrucker/updating-ideal-experiment at commit `f330ec90aa89b8b6978d9439acf8b0554b057b07`. Images and other tracked assets are included. GitHub issues, access settings, deployment services, secrets, production databases and Sciebo participant files are not copied.

The tag `reviewed-baseline-f330ec9` identifies the unchanged experiment. Setup changes add this guide, a local launcher, dependency records and push safeguards. No experiment bug fix is included in the setup commit.

## Open and run on this computer

Open PowerShell in this repository folder, then run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\sandbox.ps1 -Action Check
powershell -NoProfile -ExecutionPolicy Bypass -File .\sandbox.ps1 -Action Bots
powershell -NoProfile -ExecutionPolicy Bypass -File .\sandbox.ps1 -Action Start
```

`Bypass` applies only to that PowerShell process. It does not change the computer's saved execution policy. Start opens a local development server; visit http://localhost:8000/demo and press Ctrl+C in the terminal to stop it. No server is published on the internet by this setup. Development servers are not production hosting.

The launcher copies current application files into an ignored `.sandbox-runtime` folder before each command. Tests use a new disposable run directory. Interactive runs reuse their local test database. It removes inherited production database and cache variables for the child command and restores them afterward. Python packages are installed in this repository's ignored `.venv`. Nothing is connected to a live database. Embedded videos can still contact external video providers; video loading requires an internet connection.

After model/schema changes, use a fresh interactive test directory rather than reusing old test data. Do not run `otree resetdb` against an unspecified database. Ask for help to archive the old local test directory safely.

## Safe development process

### Temporary direct-access mode

The local branch `sandbox/fast-bug-checks` adds opt-in shortcuts. Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\sandbox.ps1 -Action Fast
```

At http://localhost:8000/demo choose a **TEST ONLY** entry and then its P1 participant link. Consent, comprehension, trial, beliefs, ideals, predictions and surveys are skipped. Synthetic fixtures are supplied instead; they are marked `sandbox_fast_test` and are not research observations. Choices are normal work at 480 seconds, normal work at 30 seconds, required ideal 0 at 30 seconds, and required ideal 5 at 30 seconds. After task submission, a result page shows the saved counts and work/leisure times. The zero-ideal defect can prevent reaching that result page; it has deliberately not been fixed.

The original task template, answer handler, timer and final-save method are unchanged. Tests with a 30-second duration check the same logic with a shorter configured window; exact 480-second claims still require the 480-second test. This mode is for the work/task bugs, not a valid test of consent, questionnaires, belief elicitation, real payments, or complete exports.

Stop the server with Ctrl+C. To return to the full route, use `-Action Start` instead of `-Action Fast`. The two modes use separate local databases. Do not reuse links from the other database. For independent tests, use a fresh private browser window to avoid the known round-only storage carryover. Keep the same tab only when deliberately testing that defect.

This temporary branch is local only. It is not pushed to GitHub or transferred to the original experiment.

#### Direct form access

The same Fast menu now includes **TEST FORMS** entries for MAIN and CONTROL separately:

- Initial belief: opens the prior-belief form directly.
- Part 1 ideal amounts and predictions: opens the original 11-column ideal table, followed by the prediction table.
- Part 2 belief and signal: opens the updated-belief form, followed by the original signal.
- Part 5 belief, ideal and prediction: opens those three final-part forms in order.
- Questionnaire 1 through 5: opens each original filler questionnaire directly.

Choose an entry, then its P1 link. These routes skip work periods, consent, comprehension and the trial. Form sessions retain the 480-second setting so their instructions still refer to 8 minutes; no work is required. Original validation, timeouts and form-saving methods remain active. The result screen lists the belief/ideal/prediction answers submitted in that route. Questionnaire-specific results are available through the local session data view; the result screen does not list all questionnaire answers.

Skipped prerequisites are supplied as explicit synthetic fixtures: prior 100, earlier performance 0, ideal 10, prediction 8 and safe risk choices. These allow pages to render but are not evidence of real choices. No payment or live study is run. Start a fresh P1 session after restarting the server; old test links may no longer exist in the local development database.

### Fix review

1. Keep `main` as the accepted sandbox setup. Start a branch for one defect, for example `fix/task-double-count`.
2. Reproduce the defect with synthetic inputs. Add a focused regression test.
3. Apply the smallest correction and run the relevant checks plus the bot suite.
4. Test the relevant browser path, including refresh, delay, stop and deadline cases.
5. Inspect the changes and record evidence. Request review before merging the fix.
6. Any transfer back to FloraDrucker's experiment, pull request there, deployment, recruitment or payment requires separate explicit consent.

Report 3 is in `sandbox-docs/report_3_experiment_bug_audit.md`. Existing passing bots do not establish that its defects are fixed. Prioritise double counting, zero-ideal completion, authoritative task validation and paid deadline counts. Keep research-design changes separate from software corrections.

## GitHub and push safeguards

`origin` must point to https://github.com/ncmnkmp/updating-ideal-experiment-sandbox.git. `source` is for reading FloraDrucker's original. Its push URL is disabled. A pre-push hook permits only the sandbox destination. Hooks are a safeguard, not a GitHub permission boundary; they can be bypassed deliberately.

After a new clone, enable the hook with:

```powershell
git config core.hooksPath .sandbox-hooks
```

Do not add participant CSV/DTA files, credentials, databases or local logs to Git. Ignore rules reduce accidents but do not remove already tracked files or replace review of staged changes.

## How to copy the experiment again

This copy is already complete. To obtain your private test copy on another computer, clone **your sandbox**, not the original:

```powershell
git clone https://github.com/ncmnkmp/updating-ideal-experiment-sandbox.git
cd updating-ideal-experiment-sandbox
git config core.hooksPath .sandbox-hooks
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r sandbox-requirements-lock.txt
```

Install Python 3.11 first on that computer. The lock records the tested Windows/Python 3.11 dependency set, not a portable lock for all operating systems. Use the launcher above after installation.

To inspect later original changes, add/fetch a read-only source remote and compare commits. Do not automatically merge them. This sandbox remains at the reviewed baseline until an update is reviewed. Do not use mirror-push for day-to-day work.

## External documentation

- GitHub repository copies: https://docs.github.com/en/repositories/creating-and-managing-repositories/duplicating-a-repository
- GitHub CLI repository creation: https://cli.github.com/manual/gh_repo_create
- oTree local setup: https://otree.readthedocs.io/en/latest/install.html

See `sandbox-docs/SETUP_VALIDATION.md` for the checks actually performed and their limits.
