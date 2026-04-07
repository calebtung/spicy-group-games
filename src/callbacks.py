"""Dash callbacks for lobby creation, joining, and live updates."""

from __future__ import annotations

import re
import uuid

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, callback_context, html, no_update
from flask import session

from src.layouts import create_home_layout, create_lobby_layout
from src.lobby_store import create_lobby, delete_lobby, join_lobby, leave_lobby, snapshot_lobby

_SESSION_PLAYER_ID = "player_id"
_SESSION_USERNAME = "username"
_SESSION_LOBBY_CODE = "lobby_code"
_CODE_PATTERN = re.compile(r"[^A-Z]")


def _normalize_code(raw_code: str | None) -> str:
    """Normalize user-entered lobby code.

    Args:
        raw_code: Input value from the homepage field.

    Returns:
        str: Uppercase alpha-only code capped to four characters.
    """
    if not raw_code:
        return ""

    upper = raw_code.upper()
    letters_only = _CODE_PATTERN.sub("", upper)
    return letters_only[:4]


def _extract_code_from_path(pathname: str | None) -> str:
    """Extract the lobby code from a URL path.

    Args:
        pathname: Current URL pathname.

    Returns:
        str: Normalized code or empty string when missing.
    """
    if not pathname:
        return ""

    prefix = "/lobby/"
    if not pathname.startswith(prefix):
        return ""

    return _normalize_code(pathname[len(prefix) :])


def _set_membership(player_id: str, username: str, code: str) -> None:
    """Persist the active player and lobby in the Flask session.

    Args:
        player_id: Stable player ID.
        username: Player display name.
        code: Active lobby code.
    """
    session[_SESSION_PLAYER_ID] = player_id
    session[_SESSION_USERNAME] = username
    session[_SESSION_LOBBY_CODE] = code


def _clear_membership() -> None:
    """Clear active lobby membership fields from session."""
    session.pop(_SESSION_LOBBY_CODE, None)
    session.pop(_SESSION_USERNAME, None)


def _require_username(username: str | None) -> tuple[bool, str]:
    """Validate username presence.

    Args:
        username: Raw username field value.

    Returns:
        tuple[bool, str]: Validity flag and cleaned username.
    """
    cleaned = (username or "").strip()
    return bool(cleaned), cleaned


def register_callbacks(app: Dash) -> None:
    """Register all Dash callbacks.

    Args:
        app: Dash application instance.
    """

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def render_page(pathname: str | None):
        """Render page content based on current URL.

        Args:
            pathname: Current URL pathname.

        Returns:
            Component: Home or lobby layout.
        """
        code = _extract_code_from_path(pathname)
        if code:
            return create_lobby_layout(code)
        return create_home_layout()

    @app.callback(
        Output("code-input", "value"),
        Output("join-button", "disabled"),
        Input("code-input", "value"),
    )
    def normalize_code_input(raw_code: str | None) -> tuple[str, bool]:
        """Clean code input and toggle join button state.

        Args:
            raw_code: Current code field value.

        Returns:
            tuple[str, bool]: Normalized code and disabled state.
        """
        code = _normalize_code(raw_code)
        join_disabled = len(code) != 4
        return code, join_disabled

    @app.callback(
        Output("url", "pathname"),
        Output("home-alert", "children"),
        Output("home-alert", "is_open"),
        Input("create-button", "n_clicks"),
        Input("join-button", "n_clicks"),
        State("username-input", "value"),
        State("code-input", "value"),
        prevent_initial_call=True,
    )
    def create_or_join_lobby(
        create_clicks: int | None,
        join_clicks: int | None,
        raw_username: str | None,
        raw_code: str | None,
    ) -> tuple[str, str, bool]:
        """Create or join a lobby from the homepage.

        Args:
            create_clicks: Create button click count.
            join_clicks: Join button click count.
            raw_username: Username field value.
            raw_code: Code field value.

        Returns:
            tuple[str, str, bool]: Redirect path, alert text, alert visibility.
        """
        trigger = callback_context.triggered_id
        if trigger not in {"create-button", "join-button"}:
            return no_update, no_update, no_update

        if trigger == "create-button" and not create_clicks:
            return no_update, no_update, no_update

        if trigger == "join-button" and not join_clicks:
            return no_update, no_update, no_update

        valid_username, username = _require_username(raw_username)
        if not valid_username:
            return no_update, "Please enter a username first.", True

        player_id = str(uuid.uuid4())

        if trigger == "create-button":
            lobby = create_lobby(host_player_id=player_id, host_username=username)
            _set_membership(player_id=player_id, username=username, code=lobby.code)
            return f"/lobby/{lobby.code}", "", False

        code = _normalize_code(raw_code)
        if len(code) != 4:
            return no_update, "Enter a valid four-letter lobby code.", True

        success, message = join_lobby(code=code, player_id=player_id, username=username)
        if not success:
            return no_update, message, True

        _set_membership(player_id=player_id, username=username, code=code)
        return f"/lobby/{code}", "", False

    @app.callback(
        Output("lobby-code-display", "children"),
        Output("players-list", "children"),
        Output("player-count", "children"),
        Output("lobby-action-button", "children"),
        Output("lobby-action-button", "color"),
        Output("lobby-alert", "children"),
        Output("lobby-alert", "is_open"),
        Output("url", "pathname", allow_duplicate=True),
        Input("lobby-interval", "n_intervals"),
        State("url", "pathname"),
        prevent_initial_call=True,
    )
    def refresh_lobby(
        n_intervals: int,
        pathname: str | None,
    ):
        """Refresh live lobby data and redirect invalid sessions home.

        Args:
            n_intervals: Number of poll ticks.
            pathname: Current URL path.

        Returns:
            tuple: Updated lobby UI state and optional redirect path.
        """
        _ = n_intervals
        code = _extract_code_from_path(pathname)
        player_id = session.get(_SESSION_PLAYER_ID)

        if not code or not player_id:
            _clear_membership()
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, "/"

        lobby = snapshot_lobby(code)
        if lobby is None:
            _clear_membership()
            return no_update, no_update, no_update, no_update, no_update, "This lobby was closed.", True, "/"

        player_ids = {pid for pid, _ in lobby.players}
        if player_id not in player_ids:
            _clear_membership()
            return no_update, no_update, no_update, no_update, no_update, "You are no longer in this lobby.", True, "/"

        list_items = []
        for pid, username in lobby.players:
            badges = []
            if pid == lobby.host_player_id:
                badges.append(dbc.Badge("Host", color="primary", className="ms-2"))
            if pid == player_id:
                badges.append(dbc.Badge("You", color="secondary", className="ms-2"))

            list_items.append(
                dbc.ListGroupItem(
                    [
                        html.Span(username),
                        *badges,
                    ]
                )
            )

        is_host = player_id == lobby.host_player_id
        action_text = "Close Lobby" if is_host else "Leave Lobby"
        action_color = "danger"

        return (
            lobby.code,
            list_items,
            f"Players: {len(lobby.players)}",
            action_text,
            action_color,
            "",
            False,
            no_update,
        )

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Input("lobby-action-button", "n_clicks"),
        State("url", "pathname"),
        prevent_initial_call=True,
    )
    def handle_lobby_action(n_clicks: int | None, pathname: str | None) -> str:
        """Handle host close and player leave actions.

        Args:
            n_clicks: Action button click count.
            pathname: Current URL path.

        Returns:
            str: Redirect target path.
        """
        if not n_clicks:
            return no_update

        code = _extract_code_from_path(pathname)
        player_id = session.get(_SESSION_PLAYER_ID)

        if not code or not player_id:
            _clear_membership()
            return "/"

        lobby = snapshot_lobby(code)
        if lobby is None:
            _clear_membership()
            return "/"

        is_host = player_id == lobby.host_player_id
        if is_host:
            delete_lobby(code)
        else:
            leave_lobby(code=code, player_id=player_id)

        _clear_membership()
        return "/"
