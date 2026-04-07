"""Dash app factory for Spicy Group Games."""

from __future__ import annotations

import os

import dash_bootstrap_components as dbc
from dash import Dash
from flask import Flask

from src.callbacks import register_callbacks
from src.layouts import create_root_layout


def create_dash_app() -> Dash:
    """Create and configure the Dash application.

    Returns:
        Dash: Configured Dash app instance.
    """
    server = Flask(__name__)
    server.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

    app = Dash(
        __name__,
        server=server,
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.FLATLY],
        title="Spicy Group Games",
    )

    app.layout = create_root_layout()
    register_callbacks(app)
    return app
