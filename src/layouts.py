"""Dash layout builders for the homepage and lobby page."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_root_layout() -> html.Div:
    """Build the root shell layout.

    Returns:
        html.Div: Top-level layout with URL routing container.
    """
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            html.Div(id="page-content"),
        ]
    )


def create_home_layout() -> dbc.Container:
    """Build the homepage layout.

    Returns:
        dbc.Container: Home screen with create/join controls.
    """
    return dbc.Container(
        [
            html.H1("Spicy Group Games", className="text-center mt-5 mb-4"),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Label("Username", html_for="username-input"),
                                dbc.Input(
                                    id="username-input",
                                    type="text",
                                    placeholder="Enter your username",
                                    debounce=True,
                                ),
                                dbc.Label(
                                    "Lobby Code",
                                    html_for="code-input",
                                    className="mt-3",
                                ),
                                dbc.Input(
                                    id="code-input",
                                    type="text",
                                    placeholder="ABCD",
                                    maxLength=4,
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Button(
                                                "Create New Lobby",
                                                id="create-button",
                                                color="success",
                                                className="w-100 mt-4",
                                            )
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "Join Lobby",
                                                id="join-button",
                                                color="primary",
                                                className="w-100 mt-4",
                                                disabled=True,
                                            )
                                        ),
                                    ],
                                    className="g-2",
                                ),
                                dbc.Alert(
                                    id="home-alert",
                                    color="danger",
                                    is_open=False,
                                    className="mt-3",
                                ),
                            ]
                        )
                    ),
                    md=6,
                    lg=5,
                ),
                justify="center",
            ),
        ],
        fluid=True,
    )


def create_lobby_layout(code: str) -> dbc.Container:
    """Build the lobby page layout.

    Args:
        code: Lobby code displayed on screen.

    Returns:
        dbc.Container: Lobby page widgets and polling interval.
    """
    return dbc.Container(
        [
            dcc.Interval(id="lobby-interval", interval=1000, n_intervals=0),
            html.H2("Lobby", className="text-center mt-4"),
            html.H1(code, id="lobby-code-display", className="text-center display-4 mb-4"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Players"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="player-count", className="mb-2"),
                                        dbc.ListGroup(id="players-list"),
                                    ]
                                ),
                            ]
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Game Configuration"),
                                dbc.CardBody(
                                    "Configuration controls will be added here in the next step."
                                ),
                            ]
                        ),
                        md=6,
                    ),
                ],
                className="g-3",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Button(
                        "Action",
                        id="lobby-action-button",
                        color="secondary",
                        className="mt-4 w-100",
                    ),
                    md=4,
                    className="mx-auto",
                )
            ),
            dbc.Alert(
                id="lobby-alert",
                color="warning",
                is_open=False,
                className="mt-3",
            ),
        ],
        fluid=True,
    )
