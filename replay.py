from pynput.mouse import Button, Controller
import time

mouse = Controller()


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1


def replay():
    f = open("path.txt", "r")
    for line in f.readlines():
        [command, x, y] = line.replace('\n', '').split(',')
        if command == 'press':
            mouse.press(Button.left)
        elif command == 'release':
            mouse.release(Button.left)

        mouse.position = (float(x), float(y))
        time.sleep(0.01)


for i in range(100):
    replay()
    print("round :", i+1, "done!")
    countdown(305)
