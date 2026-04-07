"""Data models used by the lobby system."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Lobby:
    """Represents one active lobby.

    Attributes:
        code: Immutable four-letter lobby code.
        host_player_id: Stable ID for the host's browser session.
        players: Ordered mapping of player_id to username.
        lock: Protects player mutations for this lobby.
    """

    code: str
    host_player_id: str
    players: OrderedDict[str, str] = field(default_factory=OrderedDict)
    lock: Lock = field(default_factory=Lock)
