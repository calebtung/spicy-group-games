# Spicy Group Games

Simple browser-based party game app built with Dash and Dash Bootstrap Components.

Current milestone: lobby system (create, join, live player list, host close, player leave).

## Tech Stack

- Python 3.10+
- Dash
- Dash Bootstrap Components
- Pytest

## Repository Layout

```text
.
├── .github/workflows/tests.yml
├── pyproject.toml
├── pyrightconfig.json
├── pytest.ini
├── requirements.txt
├── run_server.py
├── src/
│   └── spicy_group_games/
│       ├── __init__.py
│       ├── app.py
│       ├── callbacks.py
│       ├── layouts.py
│       ├── lobby_store.py
│       └── models.py
└── tests/
	├── conftest.py
	├── test_callbacks_helpers.py
	└── test_lobby_store.py
```

## Local Setup (Ubuntu)

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure editable install is active (recommended for development):

```bash
pip install -e .
```

Notes:
- The editable install makes the local package importable as `spicy_group_games`.
- Because editable mode links to your working tree, code changes are picked up immediately without reinstalling.
- Package source lives under src/spicy_group_games.

## Run the App

Start the Dash development server:

```bash
python run_server.py
```

Server target:
- Host: 0.0.0.0
- Port: 42069

Open a browser at:
- http://localhost:42069

## Run Unit Tests

```bash
pytest
```

Pytest configuration is defined in pytest.ini.

## GitHub CI

Unit tests run automatically on push and pull requests via:

- .github/workflows/tests.yml

Workflow summary:
- Checks out code
- Sets up Python 3.10
- Installs requirements
- Runs pytest

## Developer Notes

- This project currently uses in-memory lobby state (no database yet).
- Global lobby add/delete operations are protected by a mutex.
- Player mutations are protected by per-lobby locks.
- Code is organized in small modules to make iteration easy as game features are added.
