"""In-memory lobby storage and operations."""

from __future__ import annotations

import random
import string
from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock
from typing import Optional

from spicy_group_games.models import Lobby

_LOBBY_CODE_LENGTH = 4
_MAX_CODE_ATTEMPTS = 10_000

# This lock is only used when adding or deleting lobby entries.
_lobbies_lock = Lock()
_lobbies: OrderedDict[str, Lobby] = OrderedDict()


@dataclass(frozen=True)
class LobbySnapshot:
    """Immutable view of lobby data for rendering.

    Attributes:
        code: Four-letter lobby code.
        host_player_id: Host player's stable ID.
        players: Ordered list of (player_id, username).
    """

    code: str
    host_player_id: str
    players: list[tuple[str, str]]


def _generate_code() -> str:
    """Generate a random uppercase lobby code.

    Returns:
        str: Random four-letter uppercase code.
    """
    letters = string.ascii_uppercase
    return "".join(random.choice(letters) for _ in range(_LOBBY_CODE_LENGTH))


def create_lobby(host_player_id: str, host_username: str) -> Lobby:
    """Create and store a lobby with a unique code.

    Args:
        host_player_id: Stable ID for the host session.
        host_username: Display name for the host.

    Returns:
        Lobby: The newly created lobby object.

    Raises:
        RuntimeError: If a unique code cannot be generated.
    """
    with _lobbies_lock:
        for _ in range(_MAX_CODE_ATTEMPTS):
            code = _generate_code()
            if code in _lobbies:
                continue

            lobby = Lobby(code=code, host_player_id=host_player_id)
            lobby.players[host_player_id] = host_username
            _lobbies[code] = lobby
            return lobby

    raise RuntimeError("Unable to generate a unique lobby code.")


def get_lobby(code: str) -> Optional[Lobby]:
    """Fetch a lobby by code.

    Args:
        code: Four-letter lobby code.

    Returns:
        Optional[Lobby]: Lobby if found, otherwise None.
    """
    return _lobbies.get(code)


def delete_lobby(code: str) -> None:
    """Delete a lobby by code if it exists.

    Args:
        code: Four-letter lobby code.
    """
    with _lobbies_lock:
        _lobbies.pop(code, None)


def join_lobby(code: str, player_id: str, username: str) -> tuple[bool, str]:
    """Try to add a player to a lobby.

    Args:
        code: Lobby code to join.
        player_id: Stable ID for the joining player.
        username: Desired username.

    Returns:
        tuple[bool, str]: Success flag and optional error message.
    """
    lobby = get_lobby(code)
    if lobby is None:
        return False, "Lobby code not found."

    with lobby.lock:
        taken_names = {name.lower() for name in lobby.players.values()}
        if username.lower() in taken_names:
            return False, "That username is already in this lobby."

        lobby.players[player_id] = username

    return True, ""


def leave_lobby(code: str, player_id: str) -> None:
    """Remove a player from a lobby.

    Args:
        code: Lobby code.
        player_id: Stable ID of the player leaving.
    """
    lobby = get_lobby(code)
    if lobby is None:
        return

    with lobby.lock:
        lobby.players.pop(player_id, None)


def snapshot_lobby(code: str) -> Optional[LobbySnapshot]:
    """Read lobby data safely for UI rendering.

    Args:
        code: Lobby code to read.

    Returns:
        Optional[LobbySnapshot]: Snapshot or None if missing.
    """
    lobby = get_lobby(code)
    if lobby is None:
        return None

    with lobby.lock:
        players = list(lobby.players.items())
        return LobbySnapshot(
            code=lobby.code,
            host_player_id=lobby.host_player_id,
            players=players,
        )
