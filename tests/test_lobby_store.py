"""Unit tests for lobby storage operations."""

from __future__ import annotations

from collections import OrderedDict

from src import lobby_store


def test_create_lobby_adds_host_player() -> None:
    """Create lobby should register host and store lobby by code."""
    lobby = lobby_store.create_lobby(host_player_id="p1", host_username="Alice")

    assert len(lobby.code) == 4
    assert lobby_store.get_lobby(lobby.code) is lobby
    assert list(lobby.players.items()) == [("p1", "Alice")]


def test_create_lobby_retries_when_code_exists(monkeypatch) -> None:
    """Create lobby should skip duplicate generated codes."""
    existing = lobby_store.create_lobby(host_player_id="p1", host_username="Host")

    generated = [existing.code, "WXYZ"]

    def fake_generate_code() -> str:
        """Return deterministic values for this test."""
        return generated.pop(0)

    monkeypatch.setattr(lobby_store, "_generate_code", fake_generate_code)

    new_lobby = lobby_store.create_lobby(host_player_id="p2", host_username="Other")

    assert new_lobby.code == "WXYZ"
    assert lobby_store.get_lobby("WXYZ") is new_lobby


def test_create_lobby_raises_after_max_attempts(monkeypatch) -> None:
    """Create lobby should raise when no unique code can be found."""
    monkeypatch.setattr(lobby_store, "_MAX_CODE_ATTEMPTS", 3)
    monkeypatch.setattr(lobby_store, "_generate_code", lambda: "AAAA")

    lobby_store.create_lobby(host_player_id="p1", host_username="Host")

    try:
        lobby_store.create_lobby(host_player_id="p2", host_username="Other")
        raised = False
    except RuntimeError:
        raised = True

    assert raised is True


def test_join_lobby_rejects_missing_lobby() -> None:
    """Join should fail when the lobby code does not exist."""
    success, message = lobby_store.join_lobby(code="ABCD", player_id="p2", username="Bob")

    assert success is False
    assert message == "Lobby code not found."


def test_join_lobby_rejects_duplicate_username_case_insensitive() -> None:
    """Join should reject usernames already present in the lobby."""
    lobby = lobby_store.create_lobby(host_player_id="p1", host_username="Alice")

    success, message = lobby_store.join_lobby(code=lobby.code, player_id="p2", username="aLiCe")

    assert success is False
    assert message == "That username is already in this lobby."


def test_join_lobby_adds_player_on_success() -> None:
    """Join should append player to ordered lobby players map."""
    lobby = lobby_store.create_lobby(host_player_id="p1", host_username="Alice")

    success, message = lobby_store.join_lobby(code=lobby.code, player_id="p2", username="Bob")

    assert success is True
    assert message == ""
    assert list(lobby.players.items()) == [("p1", "Alice"), ("p2", "Bob")]


def test_leave_lobby_removes_player() -> None:
    """Leave should remove only the specified player."""
    lobby = lobby_store.create_lobby(host_player_id="p1", host_username="Alice")
    lobby_store.join_lobby(code=lobby.code, player_id="p2", username="Bob")

    lobby_store.leave_lobby(code=lobby.code, player_id="p2")

    assert list(lobby.players.items()) == [("p1", "Alice")]


def test_leave_lobby_ignores_missing_lobby() -> None:
    """Leave should be a no-op for unknown lobby code."""
    lobby_store.leave_lobby(code="NOPE", player_id="p1")


def test_delete_lobby_removes_entry() -> None:
    """Delete should remove lobby from global store."""
    lobby = lobby_store.create_lobby(host_player_id="p1", host_username="Alice")

    lobby_store.delete_lobby(lobby.code)

    assert lobby_store.get_lobby(lobby.code) is None


def test_snapshot_lobby_returns_immutable_copy_data() -> None:
    """Snapshot should include current values but not mutate source list."""
    lobby = lobby_store.create_lobby(host_player_id="p1", host_username="Alice")
    lobby_store.join_lobby(code=lobby.code, player_id="p2", username="Bob")

    snapshot = lobby_store.snapshot_lobby(lobby.code)

    assert snapshot is not None
    assert snapshot.code == lobby.code
    assert snapshot.host_player_id == "p1"
    assert snapshot.players == [("p1", "Alice"), ("p2", "Bob")]


def test_snapshot_lobby_returns_none_when_missing() -> None:
    """Snapshot should be None for unknown code."""
    assert lobby_store.snapshot_lobby("NONE") is None
