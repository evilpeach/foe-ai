import time
import cv2
import numpy as np
import mss
import numpy
from pynput.mouse import Button, Controller

templates = {
    "box": cv2.imread('idle/t_box.png'),
    "close": cv2.imread('idle/t_close.png'),
    "coin": cv2.imread('idle/t_coin.png'),
    "work": cv2.imread('idle/t_resource.png'),
    "sleep": cv2.imread('idle/t_sleep.png'),
    "sword": cv2.imread('idle/t_sword.png'),
    "produce": cv2.imread('produce/template_p_2.png'),
    "forge": cv2.imread('top/t_forge.png'),
    "ftarget": cv2.imread('top/ftarget.png'),
    "ftarget2": cv2.imread('top/ftarget_2.png'),
}


def add_offset(xy, x_offset=0, y_offset=50):
    (x, y) = xy
    return (x + x_offset, y + y_offset)


def lerp(xy1, xy2):
    (x1, y1) = xy1
    (x2, y2) = xy2
    return (x1*0.1 + x2*0.9, y1*0.1 + y1*0.9)


def lerp_iter(mouse, xy, round=50):
    (x1, y1) = mouse.position
    (x2, y2) = xy
    for i in range(0, round):
        mouse.position = (x2*(i+1)/round + (round-i-1)*x1/round,
                          y2*(i+1)/round + (round-i-1)*y1/round)
        time.sleep(0.01)
    mouse.position = xy


def dis_2(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)


def avg(arr):
    (sx, sy) = (0., 0.)
    for (x, y) in arr:
        sx += x
        sy += y
    return (sx/len(arr), sy/len(arr))


def reduce_point(points):
    if len(points) == 0:
        return []
    src = points[:]
    dst = []
    while len(src) > 0:
        a = src[0]
        src = src[1:][:]
        tbr = []
        for i in range(0, len(src)):
            if dis_2(a, src[i]) < 500:
                tbr.append(src[i])

        if len(tbr) > 0:
            dst.append(avg(tbr + [a]))
            for x in tbr:
                src.remove(x)
        else:
            dst.append(a)

    return dst


def min_x_plus_y(arr):
    min_xy = 1000_000_000_000
    xy = (0.0, 0.0)
    found = False
    for (x_, y_) in arr:
        if x_+y_ < min_xy:
            found = True
            min_xy = x_+y_
            xy = (x_, y_)
    if found:
        return xy
    return None


def match(img, template):
    w, h = template.shape[:-1]
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = .75
    loc = np.where(res >= threshold)
    return reduce_point([(pt[0]/2.+w/4., pt[1]/2.+h/4.) for pt in zip(*loc[::-1])])


with mss.mss() as sct:
    top_part = {"top": 105, "left": 540, "width": 145, "height": 65}
    mid_part = {"top": 0, "left": 0, "width": 1144, "height": 870}
    parts = [top_part, mid_part]

    looking_at = 1

    mouse = Controller()
    state = "idle"
    positions = []
    choices = []
    waiting_acc = 0

    last_time = time.time()

    while "Screen capturing":
        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

        print(
            "state: {}".format(state),
            end='\r',
            flush=True
        )

        sct_img = sct.grab(parts[looking_at])
        img = np.ascontiguousarray(numpy.array(sct_img)[:, :, 0:3])

        if state == "idle":
            close_pos = match(img, templates["close"])
            if len(close_pos) > 0:
                print("close at", close_pos[0])
                lerp_iter(mouse, close_pos[0], 10)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(1)
                last_time = time.time()
                continue

            coins = match(img, templates["coin"])
            if len(coins) > 0:
                positions = coins[:]
                state = "collect_target"
                last_time = time.time()
                continue

            works = match(img, templates["work"])
            if len(works) > 0:
                positions = works[:]
                state = "collect_target"
                continue

            boxes = match(img, templates["box"])
            if len(boxes) > 0:
                positions = boxes[:]
                state = "collect_target"
                continue

            sleeps = match(img, templates["sleep"])
            if len(sleeps) > 0:
                positions = sleeps[:]
                state = "awake"
                last_time = time.time()
                continue

            looking_at = 0
            state = "top"
            last_time = time.time()
            continue

        elif state == "top":
            if looking_at == 0:
                has_forge = len(match(img, templates["forge"])) > 0
                if has_forge:
                    print("see forge")
                    looking_at = 1
                    last_time = time.time()
                    continue
                else:
                    looking_at = 1
                    state = "idle"
                    last_time = time.time()
                    continue

            target = match(img, templates["ftarget"])
            # print("ftarget", target)
            if len(target) > 0:
                lerp_iter(mouse, add_offset(target[0], 0, 20), 20)
                mouse.press(Button.left)
                mouse.release(Button.left)
                # print("waiting for ftarget modal")
                time.sleep(3)
                looking_at = 1
                state = "looking_for_ftarget_2"
                last_time = time.time()
                continue
            else:
                looking_at = 1
                state = "idle"
                last_time = time.time()
                continue

        elif state == "looking_for_ftarget_2":
            # print("looking for ftarget 2")
            target2 = match(img, templates["ftarget2"])
            if len(target2) == 0:
                looking_at = 1
                state = "idle"
                last_time = time.time()
                continue
            lerp_iter(mouse, add_offset(target2[0], -45, 15), 30)
            mouse.press(Button.left)
            mouse.release(Button.left)
            looking_at = 1
            state = "idle"
            last_time = time.time()
            continue

        elif state == "collect_target":
            if len(positions) == 0:
                state = "idle"
                last_time = time.time()
                continue
            lerp_iter(mouse, add_offset(positions[0], 0, 40), 10)
            mouse.press(Button.left)
            mouse.release(Button.left)
            positions = positions[1:]
            last_time = time.time()
            continue

        elif state == "awake":
            if len(positions) == 0:
                state = "idle"
                last_time = time.time()
                continue
            print("awake", positions)

            lerp_iter(mouse, add_offset(positions[0]), 25)

            print("produce at ", add_offset(positions[0]))
            mouse.press(Button.left)
            mouse.release(Button.left)
            positions = positions[1:]
            waiting_acc = 0
            last_time = time.time()
            state = "produce"
            continue

        elif state == "produce":
            produces = match(img, templates["produce"])
            choices = produces[:]
            if len(choices) < 4:
                waiting_acc += time.time() - last_time
                if waiting_acc > 2.0:
                    choices = []
                    waiting_acc = 0
                    last_time = time.time()
                    state = "awake"
                continue

            waiting_acc = 0
            last_time = time.time()
            state = "select_produce"
            continue

        elif state == "select_produce":
            xy = min_x_plus_y(choices)

            if xy is None:
                choices = []
                waiting_acc = 0
                last_time = time.time()
                state = "awake"
                continue

            print("select", xy)

            lerp_iter(mouse, xy, 25)

            mouse.press(Button.left)
            mouse.release(Button.left)

            choices = []
            waiting_acc = 0
            last_time = time.time()
            state = "awake"
            continue
