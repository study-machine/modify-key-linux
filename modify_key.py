from asyncore import file_dispatcher, loop
from evdev import InputDevice, categorize, ecodes, KeyEvent, UInput

dev = InputDevice('/dev/input/event2')

modify_map = {
    # 'KEY_3': 'KEY_UP',
    # 'KEY_4': 'KEY_DOWN',

    'KEY_1': 'KEY_LEFT',
    'KEY_2': 'KEY_RIGHT',
}
need_holdings = ['KEY_RIGHTCTRL', ]


class ModifyKeyEvent(object):
    key_up = 0x0
    key_down = 0x1
    key_hold = 0x2

    def __init__(self):
        self.holding_key = set()
        self.u_input = UInput()
        # self.test()

    def test(self):
        self.inject_key('KEY_A')
        self.inject_key('KEY_B')
        self.inject_key('KEY_RIGHT')

    def is_holding(self, keycodes):
        for k in keycodes:
            if k not in self.holding_key:
                return False
        return True

    def handle_key(self, keycode, keystate):
        print 'handle_key', self.holding_key, keycode
        if keystate == self.key_hold:
            self.holding_key.add(keycode)
        elif keystate == self.key_up:
            if keycode in self.holding_key:
                self.holding_key.remove(keycode)
        elif keystate == self.key_down:
            self.keydown_event(keycode)

    def keydown_event(self, keycode):
        if self.is_holding(need_holdings):
            self.custom_direction_key(keycode)

    def custom_direction_key(self, keycode):
        self.inject_key(modify_map.get(keycode, ''))

    def inject_key(self, keycode):
        if keycode:
            code = getattr(ecodes, keycode)
            self.u_input.write(ecodes.EV_KEY, code, self.key_down)
            self.u_input.write(ecodes.EV_KEY, code, self.key_up)
            self.u_input.syn()
            print 'inject_key', self.holding_key, keycode


class InputDeviceDispatcher(file_dispatcher):
    def __init__(self, device):
        self.device = device
        file_dispatcher.__init__(self, device)
        self.modify_key = ModifyKeyEvent()

    def recv(self, ign=None):
        return self.device.read()

    def handle_read(self):
        for event in self.recv():
            key_event = categorize(event)
            if hasattr(key_event, 'keycode'):
                self.modify_key.handle_key(key_event.keycode, key_event.keystate)


if __name__ == '__main__':
    InputDeviceDispatcher(dev)
    loop()
