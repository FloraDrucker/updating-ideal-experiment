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

The checked-task repair adds model fields. The launcher now uses `interactive-checked-tasks-v1`, so older local test databases are preserved and not reused with the new schema. Start a new session and use its new links. Do not run `otree resetdb` against an unspecified database.

## Safe development process

### Fix review

1. Keep `main` as the accepted sandbox setup. Start a branch for one defect, for example `fix/task-double-count`.
2. Reproduce the defect with synthetic inputs. Add a focused regression test.
3. Apply the smallest correction and run the relevant checks plus the bot suite.
4. Test the relevant browser path, including refresh, delay, stop and deadline cases.
5. Inspect the changes and record evidence. Request review before merging the fix.
6. Any transfer back to FloraDrucker's experiment, pull request there, deployment, recruitment or payment requires separate explicit consent.

Report 3 is in `sandbox-docs/report_3_experiment_bug_audit.md`. Existing passing bots do not establish that its defects are fixed. Prioritise double counting, zero-ideal completion, authoritative task validation and paid deadline counts. Keep research-design changes separate from software corrections.

The repairs and their checks are described in `sandbox-docs/TASK_COUNT_FIX.md`, `sandbox-docs/ZERO_IDEAL_FIX.md` and `sandbox-docs/FIX_VALIDATION_2026-10-29.md`. The two repairs are separate commits on `fix/task-counts-and-zero-ideal`. This is a test branch, not permission to deploy or use real participant data.

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
