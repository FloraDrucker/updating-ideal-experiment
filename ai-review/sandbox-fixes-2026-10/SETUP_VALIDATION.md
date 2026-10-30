# Sandbox setup validation

Date: 26 October 2026.

## Source and scope

Copied the original main branch at `f330ec90aa89b8b6978d9439acf8b0554b057b07`. The baseline tag is `reviewed-baseline-f330ec9`. Application files, templates, static assets, settings and original requirements are unchanged. The setup adds a guide, launcher, push guard, this record, Report 3 and a dependency freeze. It extends ignore rules for local artifacts and participant files.

The source repository was cloned for reading. Its local remote name is `source`, with push URL `DISABLED-SOURCE-READ-ONLY`. The new remote is the independent private repository `ncmnkmp/updating-ideal-experiment-sandbox`. No original-repository write, PR, deployment or recruitment was performed.

## Checks performed

- Python 3.11.9 installed in a workspace-local runtime; isolated `.venv` created. The original `requirements.txt` installed successfully, including oTree 5.11.0. Resolved packages are recorded in `sandbox-requirements-lock.txt`.
- `sandbox.ps1 -Action Check` passed Python compilation.
- `sandbox.ps1 -Action Bots` completed with exit code 0 using the supplied 10-participant test configuration and a new disposable runtime directory.
- `sandbox.ps1 -Action Start` served the local demo at `http://localhost:8000/demo`; HTTP status 200 and the study title were verified. The temporary server was stopped, and no listener remained on port 8000.
- The pre-push hook returned failure for FloraDrucker's original URL and success for the sandbox URL. These were direct hook tests without a network push.
- Ignore checks covered `.env`, CSV/DTA files, local database files and the virtual environment.
- A diff against the baseline showed no changes under `study`, `instructions_consent`, `_static`, `_templates`, `settings.py` or `requirements.txt`.

The first restricted-process bot attempt stalled and was stopped. The same test succeeded with normal local process permissions. The first server attempt exposed a launcher PATH problem; the launcher was corrected and the local HTTP check then passed. These are setup issues, not fixes to experiment behavior.

## Remaining limits

The passing bots submit synthetic totals and do not cover the browser double-click or deadline defects. No full browser walkthrough, payment integration, network-failure test, load test, rare-condition matrix or experiment correction has been performed in this setup. The local HTTP check is not a browser test. External video providers can still receive requests when a participant page embeds their videos.

The dependency freeze records this Windows/Python 3.11 installation. It is not a security audit or a claim that these versions match the live server. Real participant records, Sciebo data, production credentials and the live database were not copied.

Use one branch and one focused test/fix at a time. Any transfer to the original repository or a live deployment requires separate consent.
