# How to Test for Prompt Injection

A vendor-neutral pytest red-team harness for prompt injection: a payload corpus across five classes (direct, indirect/second-order, jailbreak, system-prompt-leak, and data-exfiltration), four assertion helpers that judge refusal, system-prompt leak, data exfiltration, and unauthorized tool calls, a run-N-times-fail-on-any-bypass wrapper for non-deterministic model behavior, and a GitHub Actions workflow that runs a fast subset on every push and the full corpus nightly and on model bumps.

> Companion code for the Autonoma blog post: **[How to Test for Prompt Injection](https://getautonoma.com/blog/how-to-test-for-prompt-injection)**

## Requirements

Python 3.10+, plus `pytest` and `pyyaml` (both in `requirements.txt`).

**No API key and no network access are needed.** The suite ships with a built-in `FakeAppClient`, a deterministic stand-in for a real chat endpoint, so it runs immediately after a clean clone. Swap `FakeAppClient` for a client that calls your own app's preview or staging environment to red-team the real thing.

## Quickstart

```bash
git clone https://github.com/Autonoma-Tools/how-to-test-for-prompt-injection.git
cd how-to-test-for-prompt-injection
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/test_red_team.py -v
```

## Project structure

```
.github/workflows/red-team.yml
payloads/direct.yaml
payloads/indirect.yaml
payloads/jailbreak_and_leak.yaml
requirements.txt
src/assertions.py
src/harness.py
tests/test_red_team.py
```

- `payloads/` — the YAML payload corpus, one file per group of injection classes: direct, indirect (second-order), jailbreak, system-prompt-leak, and data-exfiltration. Each payload carries an `id`, a `class`, a `tier` (`fast` or `full`), and a delivery `vector`.
- `src/harness.py` — delivery and capture only. It builds the right input shape for a payload's vector and returns a structured `RedTeamResult`. It never judges pass or fail.
- `src/assertions.py` — the four assertion helpers that do the judging: refusal, system-prompt leak, data exfiltration, and unauthorized tool calls.
- `tests/test_red_team.py` — the pytest suite, including `run_n_times` and the built-in `FakeAppClient`.
- `.github/workflows/red-team.yml` — CI: the fast subset on every push, the full corpus nightly and on model bumps.

## Expected result: 25 pass, 1 deliberate failure

A clean clone reports **25 passing payload cases and one failure, `jailbreak-002`**:

```
FAILED tests/test_red_team.py::test_full_corpus_never_bypasses_guardrails[jailbreak-002]
1 failed, 25 passed
```

That failure is intentional and deterministic, not flakiness in the suite. `FakeAppClient` is written to comply with `jailbreak-002` on exactly the third of its five calls, which is the article's central claim made executable: a payload that gets through once in five runs is a real, reportable failure, because an attacker with repeated attempts only needs one bypass.

This is why `run_n_times` in `tests/test_red_team.py` fails on **any** bypass across N runs rather than on a majority or an average. Assert on the worst run, never the mean. Set `RED_TEAM_RUNS` to change N (default `5`).

## About

This repository is maintained by [Autonoma](https://getautonoma.com) as reference material for the linked blog post. Autonoma builds autonomous AI agents that plan, execute, and maintain end-to-end tests directly from your codebase.

If something here is wrong, out of date, or unclear, please [open an issue](https://github.com/Autonoma-Tools/how-to-test-for-prompt-injection/issues/new).

## License

Released under the [MIT License](./LICENSE) © 2026 Autonoma Labs.
