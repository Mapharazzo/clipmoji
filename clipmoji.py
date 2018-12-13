import emoji
import pyperclip
from pynput.keyboard import Key, KeyCode, Listener, Controller
from string import printable
from threading import Timer


# listens to keys until combination
# state = 0 - dont keep track
# state = 1 - keep the keystrokes

DICT_SPECIAL = {'`': '~',
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
                '/': '?'}


class Clipmoji:
    def __init__(self):
        self.listener = Listener(
            on_press=self.on_press, on_release=self.on_release)
        self.controller = Controller()
        self.state = False
        self._shift = False
        self._aux_backspace = False
        self.captured = ''
        self._combination = {Key.ctrl_l, Key.alt_l}
        self._special = {Key.ctrl_l, Key.alt_l, Key.shift}
        self._quit_combination = {Key.ctrl_l, Key.alt_l, Key.shift}
        self._current = set()

    def on_press(self, key):
        # print(key, self.state, self._current)
        # print(self.captured)
        if key == Key.shift or key == Key.shift_r:
            self._shift = True
        if key in self._combination:
            self._current.add(key)
            if all(k in self._current for k in self._combination):
                if self.state:
                    self.copy_to_clipboard(self.emojify_captured())
                    self.captured = ''
                    r = Timer(0.3, self.paste_to_cursor)
                    r.start()

                self._current.clear()
                self.state = not self.state
        if self.state:
            if type(key) == KeyCode and key.char in set(printable):
                if self._shift and key.char in DICT_SPECIAL.keys():
                    self.captured += DICT_SPECIAL[key.char]
                elif self._shift:
                    self.captured += key.char.upper()
                else:
                    self.captured += key.char
                self._aux_backspace = True
                self.controller.press(Key.backspace)
            elif key == Key.backspace:
                if not self._aux_backspace:
                    self.captured = self.captured[:-1]
                else:
                    self._aux_backspace = False
            elif key == Key.space:
                self.captured += ' '
                self._aux_backspace = True
                self.controller.press(Key.backspace)

    def on_release(self, key):
        if key == Key.shift or key == Key.shift_r:
            self._shift = False
        if key in self._combination and key in self._current:
            self._current.remove(key)

    def get_captured(self):
        return self.captured

    def emojify_captured(self, copy=True):
        emojify = emoji.emojize(self.captured)
        pyperclip.copy(emojify)
        return emojify

    def copy_to_clipboard(self, text):
        pyperclip.copy(text)

    def paste_to_cursor(self):
        self.controller.press(Key.ctrl)
        self.controller.press('v')
        self.controller.release('v')
        self.controller.release(Key.ctrl)


clipmojy = Clipmoji()
clipmojy.listener.start()
clipmojy.listener.join()
