#! /usr/bin/env python

import datetime
import json
import pathlib
import shutil

import pyotp
import pyperclip
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import (Button, Digits, Footer, Header, ListItem,
                             ListView, Static)

from pytotptui.qrdecode import decode_qr_code
from pytotptui.qrscreen import SelectQRImageScreen
from pytotptui.messages import MessageWidget


class TOTPCodeDisplay(Digits):
    """
    A widget to display a TOTP code.
    """


class TOTPSite(ListItem):
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
            yield Button("Copy", id="totp-copy-button")

    def on_button_pressed(self, message):
        """
        Button pressed event.
        """
        if message.button.id == "totp-copy-button":
            code = self.totp.now()
            pyperclip.copy(code)

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
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "add_with_qr_code", "Add with QR code."),
        ("c", "copy_code_to_clipboard", "Copy code to clipboard."),
        ("ctrl+x", "delete_site", "Delete TOTP site."),
        ("ctrl+s", "save_deletes", "Save deletes."),
    ]

    def compose(self) -> ComposeResult:
        """
        Create child widgets for the app.
        """
        mw = MessageWidget()
        mw.add_class("hidden")
        yield mw
        yield Header()
        yield Footer()
        urls = load_urls()
        sites = [TOTPSite(url) for url in urls]
        yield ListView(*sites, id="listview")

    def on_list_view_highlighted(self, message):
        """
        Event handler
        """
        listview = message.list_view
        for child in listview.children:
            if isinstance(child, TOTPSite):
                child.remove_class("highlighted")
        listitem = message.item
        if listitem is None:
            return
        listitem.add_class("highlighted")

    def action_toggle_dark(self) -> None:
        """
        An action to toggle dark mode.
        """
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_copy_code_to_clipboard(self):
        """
        Copy the selected code to the clipboard.
        """
        listview = self.query_one("#listview")
        listitem = listview.highlighted_child
        if listitem is None:
            return
        code = listitem.totp.now()
        pyperclip.copy(code)

    def action_delete_site(self):
        """
        Delete a site.
        """
        listview = self.query_one("#listview")
        index = listview.index
        if index is None:
            return
        listview.remove_items([index])

    def action_save_deletes(self):
        """
        Persist deletions to disk.
        """
        urls = self.get_urls_from_list_view()
        save_urls(urls)
        self.show_message("Configuration saved.")

    def action_add_with_qr_code(self):
        """
        Add a site with a QR code image.
        """
        self.push_screen(SelectQRImageScreen(), self.process_qr_code)

    def process_qr_code(self, qr_code_path):
        """
        Import a site from a QR code.
        """
        url = decode_qr_code(qr_code_path)
        listview = self.query_one("#listview")
        listview.append(TOTPSite(url))
        urls = self.get_urls_from_list_view()
        save_urls(urls)

    def get_urls_from_list_view(self):
        """
        Returns a list of URLs from the list view.
        """
        listview = self.query_one("#listview")
        urls = []
        for child in listview.children:
            if isinstance(child, TOTPSite):
                url = child.totp.provisioning_uri()
                urls.append(url)
        return urls

    def show_message(self, message, seconds=5.0):
        """
        Show a one line message floating over the middle of the application for
        `seconds` seconds.
        """
        mw = self.query_one(MessageWidget)
        mw.message = message
        mw.remove_class("hidden")

        def hideit():
            mw.add_class("hidden")

        self.set_interval(seconds, hideit, repeat=1)


def load_urls():
    """
    Load site URLs.
    """
    path = pathlib.Path("~/.config/pytotptui/sites.json").expanduser()
    with open(path, "r") as f:
        urls = json.load(f)
    return urls


def save_urls(urls):
    """
    Save URLs.
    """
    path = pathlib.Path("~/.config/pytotptui/sites.json").expanduser()
    backup_path = pathlib.Path("~/.config/pytotptui/sites.backup.json").expanduser()
    shutil.copy2(path, backup_path)
    with open(path, "w") as f:
        json.dump(urls, f, indent=4)


if __name__ == "__main__":
    app = TOTPApp()
    app.run()
