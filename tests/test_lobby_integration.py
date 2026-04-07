"""Browser integration tests for the Dash lobby UI."""

from __future__ import annotations

import re
import shutil

import pytest

from spicy_group_games.app import create_dash_app

_HAS_BROWSER_DEPS = bool(shutil.which("google-chrome") or shutil.which("chromium-browser") or shutil.which("chromium")) and bool(shutil.which("chromedriver"))
pytestmark = pytest.mark.skipif(not _HAS_BROWSER_DEPS, reason="Chrome/Chromedriver not found for Dash integration tests.")


@pytest.mark.integration
def test_join_button_enables_and_disables_while_typing(dash_duo) -> None:
    """Join button should react immediately as the lobby code is edited.

    Args:
        dash_duo: Dash testing fixture providing a browser and app runner.
    """
    app = create_dash_app()
    dash_duo.start_server(app)

    code_input = dash_duo.find_element("#code-input")
    join_button = dash_duo.find_element("#join-button")

    assert join_button.is_enabled() is False

    code_input.send_keys("ABCD")
    dash_duo.wait_for_text_to_equal("#code-input", "ABCD")
    dash_duo.wait_for_condition(lambda: dash_duo.find_element("#join-button").is_enabled(), timeout=3)

    code_input.send_keys("\b")
    dash_duo.wait_for_text_to_equal("#code-input", "ABC")
    dash_duo.wait_for_condition(lambda: not dash_duo.find_element("#join-button").is_enabled(), timeout=3)


@pytest.mark.integration
def test_create_lobby_redirects_and_shows_host_badges(dash_duo) -> None:
    """Creating a lobby should redirect and render host/you badges.

    Args:
        dash_duo: Dash testing fixture providing a browser and app runner.
    """
    app = create_dash_app()
    dash_duo.start_server(app)

    username_input = dash_duo.find_element("#username-input")
    create_button = dash_duo.find_element("#create-button")

    username_input.send_keys("HostPlayer")
    create_button.click()

    dash_duo.wait_for_element("#lobby-code-display", timeout=5)
    dash_duo.wait_for_condition(lambda: "/lobby/" in dash_duo.driver.current_url, timeout=5)

    code_text = dash_duo.find_element("#lobby-code-display").text
    assert re.fullmatch(r"[A-Z]{4}", code_text)

    players_text = dash_duo.find_element("#players-list").text
    assert "HostPlayer" in players_text
    assert "Host" in players_text
    assert "You" in players_text

    action_text = dash_duo.find_element("#lobby-action-button").text
    assert action_text == "Close Lobby"
