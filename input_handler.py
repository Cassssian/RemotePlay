# input_handler.py
# Capture and replay mouse, keyboard, and gamepad events

from pynput import mouse, keyboard
import json

class InputHandler:
    def __init__(self, data_channel):
        self.dc = data_channel

    def start_capture(self):
        mouse.Listener(on_move=self._on_move, on_click=self._on_click).start()
        keyboard.Listener(on_press=self._on_press, on_release=self._on_release).start()

    def _on_move(self, x, y):
        msg = json.dumps({'type': 'mouse_move', 'x': x, 'y': y})
        self.dc.send(msg)

    def _on_click(self, x, y, button, pressed):
        msg = json.dumps({'type': 'mouse_click', 'x': x, 'y': y, 'button': button.name, 'pressed': pressed})
        self.dc.send(msg)

    def _on_press(self, key):
        msg = json.dumps({'type': 'key_press', 'key': str(key)})
        self.dc.send(msg)

    def _on_release(self, key):
        msg = json.dumps({'type': 'key_release', 'key': str(key)})
        self.dc.send(msg)
