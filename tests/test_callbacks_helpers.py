"""Unit tests for callback helper functions."""

from __future__ import annotations

from src import callbacks


def test_normalize_code_keeps_only_uppercase_letters() -> None:
    """Normalize should uppercase, strip non-letters, and cap length to four."""
    result = callbacks._normalize_code("a1b2c3d4e")

    assert result == "ABCD"


def test_normalize_code_handles_none_input() -> None:
    """Normalize should return empty string for missing input."""
    assert callbacks._normalize_code(None) == ""


def test_extract_code_from_path_for_lobby_route() -> None:
    """Extract should parse a valid lobby path into normalized code."""
    result = callbacks._extract_code_from_path("/lobby/a9b!cD")

    assert result == "ABCD"


def test_extract_code_from_path_rejects_non_lobby_route() -> None:
    """Extract should return empty value for unrelated routes."""
    assert callbacks._extract_code_from_path("/home") == ""


def test_require_username_trims_whitespace_and_validates() -> None:
    """Username helper should trim and validate non-empty strings."""
    valid, username = callbacks._require_username("  Alice  ")

    assert valid is True
    assert username == "Alice"


def test_require_username_rejects_blank_values() -> None:
    """Username helper should fail for blank/whitespace strings."""
    valid, username = callbacks._require_username("   ")

    assert valid is False
    assert username == ""
