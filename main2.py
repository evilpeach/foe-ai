import time
import cv2
import numpy as np
import mss
import numpy
import os
import sha3
import keyboard
from pynput.mouse import Button, Controller

templates = {
    "id_input": cv2.imread("user/id_input.png"),
    "start": cv2.imread("user/start.png"),
    "channel": cv2.imread("user/channel.png"),
    "close": cv2.imread("idle/t_close.png"),
    "house": cv2.imread("user/house.png"),
    "expand": cv2.imread("user/expand.png"),
    "collapse": cv2.imread("user/collapse.png"),
    "previous": cv2.imread("user/previous.png"),
    # "user": cv2.imread("user/mewmo.png"),
    "user": cv2.imread("user/momo.png"),
    # "user": cv2.imread("user/ecore.png"),
    # "user": cv2.imread("user/archa.png"),
    # "user": cv2.imread("user/kondee.png"),
    # "gb": cv2.imread("user/confuse.png"),
    # "gb": cv2.imread("user/alex.png"),
    # "gb": cv2.imread("user/alcatraz.png"),
    # "gb": cv2.imread("user/aachen.png"),
    # "gb": cv2.imread("user/chateau.png"),
    # "gb": cv2.imread("user/cape.png"),
    # "gb": cv2.imread("user/castel.png"),
    "gb": cv2.imread("user/himeji.png"),
    # "gb": cv2.imread("user/dom.png"),
    "find_fork": cv2.imread("user/find_fork.png"),
}


def add_offset(xy, x_offset=0, y_offset=50):
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


def min_x_plus_y(arr):
    min_xy = 1000_000_000_000
    xy = (0.0, 0.0)
    found = False
    for (x_, y_) in arr:
        if x_ + y_ < min_xy:
            found = True
            min_xy = x_ + y_
            xy = (x_, y_)
    if found:
        return xy
    return None


def match(img, template, threshold=0.9):
    w, h = template.shape[:-1]
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return reduce_point(
        [(pt[0] / 2.0 + w / 4.0, pt[1] / 2.0 + h / 4.0) for pt in zip(*loc[::-1])]
    )


def get_password(username):
    k = sha3.keccak_256()
    k.update(bytes(username, "utf-8"))
    return k.hexdigest()


def open_browser():
    # os.system(
    #     '''open -na "Google Chrome" --args --incognito "https://th.forgeofempires.com/page"'''
    # )
    os.system(
        '''open -a Firefox --args -private-window "https://th.forgeofempires.com/page"'''
    )


def read_file():
    arr = []
    f = open("./user/test", "r")
    for x in f.readlines():
        y, z = x.split(",")
        if y != "":
            arr += [[y, z.rstrip()]]
    f.close()
    return arr


def find_active_user(arr):
    for x in arr:
        if time.time() - int(x[1]) > 3600:
            return x
    return None


def update_users(users, updated_user):
    idx = -1
    for i, user in enumerate(users):
        if updated_user[0] == user[0]:
            idx = i
            break
    if idx == -1:
        raise ValueError("user not found")

    users[idx][1] = int(time.time())


def write_file(new_users):
    f = open("./user/test", "w")
    for user in new_users:
        f.write(str(user[0]) + "," + str(user[1]) + "\n")


with mss.mss() as sct:
    mid_part = {"top": 0, "left": 0, "width": 1300, "height": 900}

    all_users = []
    active_user = None
    mouse = Controller()
    state = "init"

    last_state = ""
    last_changed = time.time()

    while "Screen capturing":
        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

        print("state: {}".format(state), end="\r", flush=True)

        sct_img = sct.grab(mid_part)
        img = np.ascontiguousarray(numpy.array(sct_img)[:, :, 0:3])

        # check timeout
        if last_state == state and state != "init":
            if int(time.time()) - last_changed > 60:
                print("timeout!!!")
                state = "kill"
        else:
            last_state = state
            last_changed = int(time.time())

        if state == "init":
            all_users = read_file()
            active_user = find_active_user(all_users)
            if active_user == None:
                time.sleep(10)
                continue
            else:
                print("user is", active_user)
                open_browser()
                state = "login"
                continue

        elif state == "login":
            id_inputs = match(img, templates["id_input"])
            if len(id_inputs) > 0:
                # input id
                print("input at", id_inputs[0])
                lerp_iter(mouse, id_inputs[0], 10)
                mouse.press(Button.left)
                mouse.release(Button.left)
                keyboard.write(active_user[0])

                # input password
                time.sleep(2)
                lerp_iter(mouse, add_offset(id_inputs[0], 0, 50), 10)
                mouse.press(Button.left)
                mouse.release(Button.left)
                keyboard.write(get_password(active_user[0]))

                # click login
                time.sleep(2)
                lerp_iter(mouse, add_offset(id_inputs[0], 50, 135), 10)
                mouse.press(Button.left)
                mouse.release(Button.left)

                # move mouse away
                time.sleep(1)
                lerp_iter(mouse, add_offset(id_inputs[0], 200, 50), 10)
                state = "start"
                continue

        elif state == "start":
            starts = match(img, templates["start"])
            if len(starts) > 0:
                # input id
                print("start btn at", starts[0])
                time.sleep(0.5)
                lerp_iter(mouse, starts[0], 10)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                state = "channel"
                continue

        elif state == "channel":
            channels = match(img, templates["channel"])
            if len(channels) > 0:
                # input id
                print("click channel at", channels[0])
                lerp_iter(mouse, channels[0], 10)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                state = "target_user"
                continue

        elif state == "target_user":
            close_pos = match(img, templates["close"])
            if len(close_pos) > 0:
                target_gbs = match(img, templates["gb"], 0.75)
                print("close", target_gbs)
                if len(target_gbs) > 0:
                    pass
                else:
                    print("close at", close_pos[0])
                    lerp_iter(mouse, close_pos[0], 1)
                    time.sleep(0.5)
                    mouse.press(Button.left)
                    mouse.release(Button.left)
                    time.sleep(0.5)
                    continue

            users = match(img, templates["user"])
            if len(users) > 0:
                print("user at", users[0])
                # click hotel icon
                lerp_iter(mouse, add_offset(users[0], 75, 50), 3)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                lerp_iter(mouse, add_offset(users[0], 0, 20), 3)
                time.sleep(2)

                # click support
                lerp_iter(mouse, add_offset(users[0], 40, 70), 3)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                lerp_iter(mouse, add_offset(users[0], 0, 20), 3)
                time.sleep(2)

                # click gb icon
                lerp_iter(mouse, add_offset(users[0], 80, 20), 3)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                lerp_iter(mouse, add_offset(users[0], 0, 20), 3)
                time.sleep(2)
                state = "choose_gb"
                continue

            expands = match(img, templates["expand"])
            if len(expands) > 0:
                print("expand at", expands[0])
                mouse.position = expands[0]
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                lerp_iter(mouse, add_offset(expands[0], 0, 30), 3)
                continue

            previous = match(img, templates["previous"])
            if len(previous) > 0:
                print("previous at", previous[0])
                mouse.position = add_offset(previous[0], 0, 0)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                lerp_iter(mouse, add_offset(previous[0], 0, -200), 10)
                time.sleep(0.5)
                continue

        elif state == "choose_gb":
            target_gbs = match(img, templates["gb"], 0.75)
            print(target_gbs)
            if len(target_gbs) > 0:
                print("target_gb at", target_gbs[0])
                lerp_iter(mouse, add_offset(target_gbs[0], 600, -20), 5)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                lerp_iter(mouse, add_offset(target_gbs[0], 0, 30), 5)
                time.sleep(0.5)
                state = "find_fork"
                continue
            else:
                state = "target_user"

        elif state == "find_fork":
            find_forks = match(img, templates["find_fork"])
            if len(find_forks) > 0:
                print("find_forks at", find_forks[0])
                lerp_iter(mouse, add_offset(find_forks[0], -30, 10), 10)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(3)
                update_users(all_users, active_user)
                write_file(all_users)
                state = "kill"
                continue

        elif state == "kill":
            # os.system("killall -9 'Google Chrome'")
            os.system("pkill -f firefox")
            time.sleep(2)
            state = "init"
            continue

