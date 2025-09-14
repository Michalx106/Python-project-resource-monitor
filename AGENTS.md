# Repository Guidelines

This document describes how to work on this repository and contribute changes efficiently and safely.

## Project Structure & Module Organization
- Root entrypoint: `main.py` (Tkinter UI + Matplotlib charts).
- Monitors: `monitor/` (CPU, RAM, Disk, GPU, shared base and utils).
- Export: `exporter/` (CSV exporters for individual and multi-metric data).
- Virtual env (local): `myenv/` is user-specific and ignored; do not commit.
- Tests: none yet; add under `tests/` when contributing tests.

## Build, Test, and Development Commands
- Create env: `python3 -m venv .venv && source .venv/bin/activate`.
- Install deps: `pip install -r requirements.txt`.
- Run app (GUI): `python main.py`.
- Optional (Mac): if GPU not detected, app still runs without GPU plots.

## Coding Style & Naming Conventions
- Python, PEP 8 with 4‑space indentation; keep lines readable (~100–120 chars).
- Modules/files: `snake_case.py`; classes: `PascalCase`; functions/vars: `snake_case`.
- Use type hints for public functions and data classes; prefer small, focused modules.
- Keep UI labels consistent with current language used in the app.
- Avoid side effects on import; place runtime code under `if __name__ == "__main__":`.

## Testing Guidelines
- Framework: use `pytest` (add to `requirements.txt` when introducing tests).
- Location: `tests/` with files named `test_*.py`.
- Focus: unit tests for monitors and exporters; stub GPU backends when unavailable.
- Aim for clear, deterministic tests; add basic coverage for new features.

## Commit & Pull Request Guidelines
- Commit style: history shows short topic commits (e.g., `+gpuMonitor`). Prefer Conventional Commits going forward, e.g., `feat: add GPU monitor` or `fix: handle disk permission errors`.
- One logical change per commit; keep messages imperative and specific.
- PRs: include a concise description, linked issue (if any), run/verify steps, and screenshots or CLI output when UI/CSV changes are relevant.
- Ensure `python main.py` runs cleanly and new dependencies are listed in `requirements.txt`.

## Security & Configuration Tips
- Do not commit secrets or local environments; keep `.venv/` and `myenv/` ignored.
- Disk queries may raise permission errors—handle gracefully as in existing code.
- GPU support is optional; code should degrade safely when backends are missing.
