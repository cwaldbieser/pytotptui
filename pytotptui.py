#! /usr/bin/env python

import datetime
import json
import pathlib

import pyotp
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Digits, Footer, Header, Static


class TOTPCodeDisplay(Digits):
    """
    A widget to display a TOTP code.
    """


class TOTPSite(Static):
    """
    A widget that shows the TOTP code for a site.
    """

    def __init__(self, url, *args, **kwds):
        """
        Initialize widget.
        """
        super().__init__(*args, **kwds)
        self.totp = pyotp.parse_uri(url)

    def on_mount(self) -> None:
        """
        Event handler called when widget is added to the app.
        """
        self.set_interval(1, self.update_totp)

    def compose(self) -> ComposeResult:
        """
        Create child widgets.
        """
        totp = self.totp
        now = totp.now()
        name = totp.name
        if name is None:
            name = ""
        issuer = totp.issuer
        if issuer is None:
            issuer = ""
        with Horizontal():
            time_remaining = (
                totp.interval - datetime.datetime.now().timestamp() % totp.interval
            )
            yield Static(issuer, id="totp-issuer")
            yield Static(name, id="totp-name")
            yield Static(f"{int(round(time_remaining, 0))} s", id="totp-time-remaining")
            yield TOTPCodeDisplay(now, id="totp-display")

    def update_totp(self) -> None:
        """
        Method to update the time remaining and code.
        """
        totp = self.totp
        time_remaining = (
            totp.interval - datetime.datetime.now().timestamp() % totp.interval
        )
        totp_code_display = self.query_one("#totp-display")
        totp_code_display.update(totp.now())
        time_display = self.query_one("#totp-time-remaining")
        time_display.update(f"{int(round(time_remaining, 0))} s")


class TOTPApp(App):
    """
    A Textual app to manage TOTP codes.
    """

    CSS_PATH = "totp.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        urls = load_urls()
        sites = [TOTPSite(url) for url in urls]
        yield VerticalScroll(*sites, id="vscroll")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


def load_urls():
    """
    Load site URLs.
    """
    path = pathlib.Path("~/.config/pytotptui/sites.json").expanduser()
    with open(path, "r") as f:
        urls = json.load(f)
    return urls


if __name__ == "__main__":
    app = TOTPApp()
    app.run()
