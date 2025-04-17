# input_handler.py
# Capture and replay mouse, keyboard, and gamepad events

from pynput import mouse, keyboard
import json
import pygame
import sys

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

class XboxControllerHandler:
    def __init__(self, data_channel):
        self.dc = data_channel
        pygame.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    def capture_events(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                msg = json.dumps({
                    'type': 'joystick_axis',
                    'axis': event.axis,
                    'value': event.value
                })
                self.dc.send(msg)
            elif event.type == pygame.JOYBUTTONDOWN:
                msg = json.dumps({
                    'type': 'joystick_button',
                    'button': self._map_button(event.button),
                    'pressed': True
                })
                self.dc.send(msg)
            elif event.type == pygame.JOYBUTTONUP:
                msg = json.dumps({
                    'type': 'joystick_button',
                    'button': self._map_button(event.button),
                    'pressed': False
                })
                self.dc.send(msg)
            elif event.type == pygame.JOYHATMOTION:
                msg = json.dumps({
                    'type': 'joystick_hat',
                    'hat': event.hat,
                    'value': event.value
                })
                self.dc.send(msg)

    def _map_button(self, button):
        # Mapping des boutons Xbox
        button_map = {
            0: 'A',
            1: 'B',
            2: 'X',
            3: 'Y',
            4: 'LB',
            5: 'RB',
            6: 'View',
            7: 'Start',
            8: 'Left Stick',
            9: 'Right Stick',
            10: 'Xbox',
            11: 'Share'
        }
        return button_map.get(button, f'Unknown({button})')

    def has_gyroscope(self):
        # Xbox controllers typically do not have gyroscopes
        return False

class PlayStationControllerHandler:
    def __init__(self, data_channel):
        self.dc = data_channel
        pygame.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    def capture_events(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                msg = json.dumps({
                    'type': 'joystick_axis',
                    'axis': event.axis,
                    'value': event.value
                })
                self.dc.send(msg)
            elif event.type == pygame.JOYBUTTONDOWN:
                msg = json.dumps({
                    'type': 'joystick_button',
                    'button': self._map_button(event.button),
                    'pressed': True
                })
                self.dc.send(msg)
            elif event.type == pygame.JOYBUTTONUP:
                msg = json.dumps({
                    'type': 'joystick_button',
                    'button': self._map_button(event.button),
                    'pressed': False
                })
                self.dc.send(msg)
            elif event.type == pygame.JOYHATMOTION:
                msg = json.dumps({
                    'type': 'joystick_hat',
                    'hat': event.hat,
                    'value': event.value
                })
                self.dc.send(msg)

    def _map_button(self, button):
        # Mapping des boutons PlayStation
        button_map = {
            0: 'Cross',
            1: 'Circle',
            2: 'Square',
            3: 'Triangle',
            4: 'L1',
            5: 'R1',
            6: 'Share',
            7: 'Options',
            8: 'PS',
            9: 'Left Stick',
            10: 'Right Stick'
        }
        return button_map.get(button, f'Unknown({button})')

    def has_gyroscope(self):
        # PlayStation controllers (e.g., DualShock 4, DualSense) have gyroscopes
        return True

    def capture_gyroscope(self):
        # Simulate gyroscope data (requires additional libraries for real data)
        gyroscope_data = {
            'type': 'gyroscope',
            'x': 0.0,  # Replace with actual gyroscope data
            'y': 0.0,
            'z': 0.0
        }
        msg = json.dumps(gyroscope_data)
        self.dc.send(msg)

if __name__ == "__main__":
    # Initialisation de pygame
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Test Input Handler")
    font = pygame.font.Font(None, 36)

    # Initialisation des manettes
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        controller_type = "Xbox" if "Xbox" in joystick.get_name() else "PlayStation"
    else:
        joystick = None
        controller_type = "None"

    manette = XboxControllerHandler(None) if controller_type == "Xbox" else PlayStationControllerHandler(None)

    # Fonction pour afficher le texte
    def display_text(text):
        screen.fill((0, 0, 0))  # Efface l'écran
        rendered_text = font.render(text, True, (255, 255, 255))
        screen.blit(rendered_text, (20, 130))
        pygame.display.flip()

    display_text("Press any key or button...")

    # Boucle principale
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                display_text(f"Key Pressed: {pygame.key.name(event.key)}")
            elif event.type == pygame.JOYBUTTONDOWN:
                display_text(f"Joystick Button: {manette._map_button(event.button)}")
            # elif event.type == pygame.JOYAXISMOTION:
            #     display_text(f"Axis {event.axis}: {event.value:.2f}")
            elif event.type == pygame.JOYHATMOTION:
                display_text(f"Hat {event.hat}: {event.value}")

    pygame.quit()
    sys.exit()
