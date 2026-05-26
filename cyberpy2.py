from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.document import Document
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style

from pygments.lexers import PythonLexer

import sys
import os
import re


# =============================================================================
# 🎨 CYBERPUNK MUTED THEME
# =============================================================================

CYBERPUNK_STYLE = Style.from_dict({

    # -------------------------------------------------------------------------
    # GENERALE
    # -------------------------------------------------------------------------
    "":                              "#d0d0d0",

    "frame.border":                 "#5a5a5a",
    "frame.label":                  "bold #4f8f9f",

    "status":                       "bg:#1a1a1a #4f8f9f",

    "line-number":                  "#5a5a5a",
    "line-number.current":          "bold #c07a3a",

    "cursor-line":                  "bg:#1f1f1f",

    # -------------------------------------------------------------------------
    # SYNTAX HIGHLIGHTING
    # -------------------------------------------------------------------------
    "pygments.text":                "#d0d0d0",

    # keywords
    "pygments.keyword":             "bold #c07a3a",
    "pygments.keyword.control":     "bold #c65a5a",

    # nomi
    "pygments.name":                "#d0d0d0",
    "pygments.name.function":       "#db6c2c",
    "pygments.name.namespace":      "#98e080",
    "pygments.name.class":          "bold #b08a3c",

    # stringhe
    "pygments.string":              "#a68b4a",

    # numeri
    "pygments.number":              "#b08a3c",

    # operatori
    "pygments.operator":            "#8a8a8a",
    "pygments.punctuation":         "#8a8a8a",

    # commenti
    "pygments.comment":             "italic #5a5a5a",

    # errori
    "pygments.error":               "bg:#a84a4a #ffffff",

})


# =============================================================================
# AUTOCOMPLETE BASE
# =============================================================================

BASE_WORDS = [
    "def", "class", "import", "from", "return", "for", "while",
    "if", "elif", "else", "try", "except", "with", "as",
    "print", "len", "range", "open", "self", "True", "False",
    "None", "append", "insert", "remove", "dict", "list",
    "set", "tuple"
]


# =============================================================================
# IDE
# =============================================================================

class CyberCodeEditor:

    def __init__(self, filename=None):

        self.filename = filename
        self.mode = "INSERT"

        # ---------------------------------------------------------------------
        # EDITOR
        # ---------------------------------------------------------------------
        self.text_area = TextArea(
            text=self.load_file(),
            lexer=PygmentsLexer(PythonLexer),

            scrollbar=True,
            line_numbers=True,
            wrap_lines=False,

            auto_suggest=AutoSuggestFromHistory(),

            style="",
        )

        # ---------------------------------------------------------------------
        # STATUS BAR
        # ---------------------------------------------------------------------
        self.status = TextArea(
            text=self.status_text(),
            height=1,
            focusable=False,
            style="class:status",
        )

        # ---------------------------------------------------------------------
        # ROOT LAYOUT
        # ---------------------------------------------------------------------
        self.root = HSplit([
            Frame(
                self.text_area,
                title="⚡ CYBERCODE PRO IDE | TAB autocomplete | Ctrl-S save | Ctrl-Q quit"
            ),
            self.status
        ])

        # ---------------------------------------------------------------------
        # KEYBINDINGS
        # ---------------------------------------------------------------------
        self.kb = self.bind_keys()

        # ---------------------------------------------------------------------
        # APPLICATION
        # ---------------------------------------------------------------------
        self.app = Application(
            layout=Layout(self.root),
            key_bindings=self.kb,
            full_screen=True,
            style=CYBERPUNK_STYLE,
        )

    # =========================================================================
    # FILE MANAGEMENT
    # =========================================================================

    def load_file(self):

        if self.filename and os.path.exists(self.filename):

            with open(self.filename, "r", encoding="utf-8") as f:
                return f.read()

        return ""

    def save_file(self):

        if not self.filename:
            self.filename = "output.py"

        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(self.text_area.text)

        self.status.text = f"💾 Salvato: {self.filename}"

    # =========================================================================
    # STATUS BAR
    # =========================================================================

    def status_text(self):

        return (
            f"[{self.mode}] "
            f"file: {self.filename or 'nuovo.py'}"
        )

    # =========================================================================
    # SMART AUTOCOMPLETE
    # =========================================================================

    def extract_words(self):

        text = self.text_area.text

        words = set(BASE_WORDS)

        # Estrai tutte le parole del file
        for w in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text):
            words.add(w)

        return list(words)

    def autocomplete(self):

        doc = self.text_area.document

        word = doc.get_word_before_cursor()

        if not word:
            return

        words = self.extract_words()

        matches = [
            w for w in words
            if w.startswith(word) and w != word
        ]

        if matches:

            completion = sorted(matches)[0]

            new_text = (
                doc.text_before_cursor[:-len(word)]
                + completion
                + doc.text_after_cursor
            )

            self.text_area.buffer.document = Document(
                new_text,
                cursor_position=(
                    doc.cursor_position
                    - len(word)
                    + len(completion)
                )
            )

    # =========================================================================
    # MODALITÀ VIM-LIKE
    # =========================================================================

    def toggle_mode(self):

        if self.mode == "INSERT":
            self.mode = "NORMAL"
        else:
            self.mode = "INSERT"

        self.status.text = self.status_text()

    # =========================================================================
    # KEYBINDINGS
    # =========================================================================

    def bind_keys(self):

        kb = KeyBindings()

        # ---------------------------------------------------------------------
        # SAVE
        # ---------------------------------------------------------------------
        @kb.add("c-s")
        def _(event):

            self.save_file()

        # ---------------------------------------------------------------------
        # QUIT
        # ---------------------------------------------------------------------
        @kb.add("c-q")
        def _(event):

            event.app.exit()

        # ---------------------------------------------------------------------
        # AUTOCOMPLETE
        # ---------------------------------------------------------------------
        @kb.add("tab")
        def _(event):

            self.autocomplete()

        @kb.add("c-space")
        def _(event):

            self.autocomplete()

        # ---------------------------------------------------------------------
        # TOGGLE MODE
        # ---------------------------------------------------------------------
        @kb.add("escape")
        def _(event):

            self.toggle_mode()

        # ---------------------------------------------------------------------
        # RELOAD FILE
        # ---------------------------------------------------------------------
        @kb.add("c-r")
        def _(event):

            self.text_area.text = self.load_file()

            self.status.text = "↻ File ricaricato"

        return kb

    # =========================================================================
    # RUN
    # =========================================================================

    def run(self):

        self.app.run()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    file = sys.argv[1] if len(sys.argv) > 1 else None

    CyberCodeEditor(file).run()