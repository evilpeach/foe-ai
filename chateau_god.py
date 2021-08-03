import time
import cv2
import mss
import numpy as np
from pynput.mouse import Button, Controller

templates = {
    "cancel": cv2.imread("chateau_loop/cancel.png"),
    "bag": cv2.imread("chateau_loop/bag.png"),
    "collect": cv2.imread("chateau_loop/collect.png"),
}


def add_offset(xy, x_offset=0, y_offset=0):
    (x, y) = xy
    return (x + x_offset, y + y_offset)


def lerp(xy1, xy2):
    (x1, y1) = xy1
    (x2, y2) = xy2
    return (x1 * 0.1 + x2 * 0.9, y1 * 0.1 + y1 * 0.9)


def lerp_iter(mouse, xy, round=50):
    (x1, y1) = mouse.position
    (x2, y2) = xy
    for i in range(0, round):
        mouse.position = (
            x2 * (i + 1) / round + (round - i - 1) * x1 / round,
            y2 * (i + 1) / round + (round - i - 1) * y1 / round,
        )
        time.sleep(0.01)
    mouse.position = xy


def dis_2(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)


def avg(arr):
    (sx, sy) = (0.0, 0.0)
    for (x, y) in arr:
        sx += x
        sy += y
    return (sx / len(arr), sy / len(arr))


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


def match(img, template, threshold=0.9):
    w, h = template.shape[:-1]
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return reduce_point(
        [(pt[0] / 2.0 + w / 4.0, pt[1] / 2.0 + h / 4.0) for pt in zip(*loc[::-1])]
    )


with mss.mss() as sct:
    scope = {"top": 140, "left": 0, "width": 800, "height": 800}
    mouse = Controller()
    count = 0

    while "Screen capturing":
        print("Count: ", count)
        sct_img = sct.grab(scope)
        img = np.ascontiguousarray(np.array(sct_img)[:, :, 0:3])

        bags = match(img, templates["bag"])
        collects = match(img, templates["collect"])
        cancels = match(img, templates["cancel"])

        if len(bags) > 0:
            print("found bags", bags)
            for bag in bags:
                lerp_iter(mouse, add_offset(bag, 0, 130), 10)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)

        elif len(collects) > 0:
            print("found collect", collects)
            lerp_iter(mouse, add_offset(collects[0], 0, 120), 10)
            mouse.press(Button.left)
            mouse.release(Button.left)
            count = count+1
            time.sleep(0.5)

        elif len(cancels) > 0:
            print("found cancel", cancels)
            lerp_iter(mouse, add_offset(cancels[0], 0, 120), 10)
            mouse.press(Button.left)
            mouse.release(Button.left)
            time.sleep(1.8)
        else:
            print("finding...")
            time.sleep(0.7)
            mouse.position = (50, 550)
            mouse.press(Button.left)
            mouse.release(Button.left)
