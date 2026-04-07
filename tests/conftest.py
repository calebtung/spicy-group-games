"""Shared pytest fixtures for unit tests."""

from __future__ import annotations

import pytest

from src import lobby_store


@pytest.fixture(autouse=True)
def clear_lobby_store() -> None:
    """Reset global in-memory lobbies before and after each test.

    This keeps tests independent because the production store is module-level
    process state.
    """
    with lobby_store._lobbies_lock:
        lobby_store._lobbies.clear()
    yield
    with lobby_store._lobbies_lock:
        lobby_store._lobbies.clear()
