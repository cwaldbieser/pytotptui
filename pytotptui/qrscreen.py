import pathlib

from textual.screen import ModalScreen
from textual.containers import Grid
from textual.widgets import DirectoryTree, Input, Button


class SelectQRImageScreen(ModalScreen):
    """
    Screen for selecting QR code image.
    """

    def compose(self):
        """
        Widgets for this screen.
        """
        path = pathlib.Path("~/").expanduser()
        with Grid(id="qr-dialog"):
            yield DirectoryTree(path, id="qr-file-tree")
            yield Input(id="qr-path-input", value="xyzzy")
            yield Button("OK", id="qr-ok-button", classes="qr-dialog-button")
            yield Button("Cancel", id="qr-cancel-button", classes="qr-dialog-button")

    def on_directory_tree_file_selected(self, message):
        """
        Event handler for file selected event.
        """
        input = self.query_one("#qr-path-input")
        input.value = str(message.path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "qr-ok-button":
            input = self.query_one("#qr-path-input")
            self.dismiss(input.value)
        else:
            self.dismiss(None)
