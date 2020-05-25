from pynput import keyboard, mouse


class Test:
    def __init__(self):
        self.is_recording = False
        self.is_pressed = False
        self.mouse_actions = []
        self.mouse = mouse.Listener(
            on_move=self.on_move, on_click=self.on_click)

    def on_click(self, x, y, button, pressed):
        if not self.is_recording:
            # Stop listener
            return False
        if pressed:
            self.mouse_actions.append(('press', x, y))
            self.is_pressed = True
        else:
            self.mouse_actions.append(('release', x, y))
            self.is_pressed = False

    def on_move(self, x, y):
        if self.is_pressed:
            self.mouse_actions.append(('press', x, y))
        else:
            self.mouse_actions.append(('move', x, y))

    def on_release(self, key):
        print('{0} released'.format(
            key))
        if '{0}'.format(key) == "'p'":
            if not self.is_recording:
                self.is_recording = True
                self.mouse_actions = []
                self.mouse.start()
                print('start record')
            else:
                self.is_recording = False
                f = open("path.txt", "w")
                for action in self.mouse_actions:
                    f.write('{0},{1},{2}\n'.format(
                        action[0], action[1], action[2])
                    )
                f.close()
                print('stop record')

        if key == keyboard.Key.esc:
            # Stop listener
            return False


t = Test()
with keyboard.Listener(on_release=t.on_release) as listener:
    print('live!')
    listener.join()
