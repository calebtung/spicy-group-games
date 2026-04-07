"""Development entrypoint for running the Dash server."""

from spicy_group_games.app import create_dash_app


def main() -> None:
    """Start the Dash development server.

    The app listens on all interfaces so it is easy to test from other
    devices on the same network.
    """
    app = create_dash_app()
    app.run(host="0.0.0.0", port=42069, debug=True)


if __name__ == "__main__":
    main()
