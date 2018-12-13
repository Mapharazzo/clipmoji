from string import printable
from threading import Timer

from pynput.keyboard import Key, KeyCode, Listener, Controller
import emoji
import pyperclip

DICT_SPECIAL = {
    '`': '~',
    '1': '!',
    '2': '@',
    '3': '#',
    '4': '$',
    '5': '%',
    '6': '^',
    '7': '&',
    '8': '*',
    '9': '(',
    '0': ')',
    '-': '_',
    '=': '+',
    '[': '{',
    ']': '}',
    '\\': '|',
    ';': ':',
    "'": '"',
    ',': '<',
    '.': '>',
    '/': '?'
}


class Clipmoji:
    def __init__(self):
        self.listener = Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.controller = Controller()

        self.trigger_shortcuts = set([
            (Key.ctrl_l, Key.alt_l),
            (Key.ctrl_r, Key.alt_r)
        ])
        self.shortcut_to_exact_match_mapping = dict([
            (shortcut, False) for shortcut in self.trigger_shortcuts
        ])

        self.keys_pressed = []
        self.is_recording = False

        self.keys_captured = ''

        # TODO: da fuck is dis Andrei?
        self._aux_backspace = False

    def on_press(self, key):
        if key not in self.keys_pressed:
            self.keys_pressed.append(key)

        keys_pressed = tuple(self.keys_pressed)
        for shortcut in self.shortcut_to_exact_match_mapping.keys():
            self.shortcut_to_exact_match_mapping.update({
                shortcut: shortcut == keys_pressed
            })

        if self.is_recording:
            if type(key) == KeyCode and key.char in set(printable):
                if self.is_shift_pressed(key) and key.char in DICT_SPECIAL.keys():
                    self.keys_captured += DICT_SPECIAL[key.char]
                elif self.is_shift_pressed(key):
                    self.keys_captured += key.char.upper()
                else:
                    self.keys_captured += key.char
                self._aux_backspace = True
                self.controller.press(Key.backspace)
                self.controller.release(Key.backspace)
            elif key == Key.backspace:
                if not self._aux_backspace:
                    self.keys_captured = self.keys_captured[:-1]
                else:
                    self._aux_backspace = False
            elif key == Key.space:
                self.keys_captured += ' '
                self._aux_backspace = True
                self.controller.press(Key.backspace)
                self.controller.release(Key.backspace)

    def is_shift_pressed(self, key):
        return Key.shift_l in self.keys_pressed or Key.shift_r in self.keys_pressed

    def on_release(self, key):
        for shortcut, is_exact_match in self.shortcut_to_exact_match_mapping.items():
            if shortcut in self.trigger_shortcuts and is_exact_match:
                if self.is_recording:
                    emojified = emoji.emojize(self.keys_captured)
                    pyperclip.copy(emojified)

                    self.keys_captured = ''

                    timer = Timer(0.3, self.paste_to_cursor)
                    timer.start()

                self.shortcut_to_exact_match_mapping.update({
                    shortcut: False
                })
                self.is_recording = not self.is_recording

        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def paste_to_cursor(self):
        with self.controller.pressed(Key.ctrl):
            self.controller.press('v')
            self.controller.release('v')
