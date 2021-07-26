import time
import cv2
import numpy as np
import mss
import numpy
import random
from pynput.mouse import Button, Controller

templates = {
    "nego": cv2.imread("nego/start.png"),
    "choose": cv2.imread("nego/choose.png"),
    "answer": cv2.imread("nego/answer2.png"),
    "send": cv2.imread("nego/send.png"),
    "correct": cv2.imread("nego/correct.png"),
    "incorrect": cv2.imread("nego/incorrect.png"),
    "wrong-person": cv2.imread("nego/wrong-person.png"),
    "topup": cv2.imread("nego/topup.png"),
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
    return reduce_point([(pt[0] / 2.0 + w / 4.0, pt[1] / 2.0 + h / 4.0) for pt in zip(*loc[::-1])])


with mss.mss() as sct:
    scope = {"top": 0, "left": 0, "width": 1400, "height": 1000}
    mouse = Controller()
    state = "init"
    questions = None
    answers = None
    possible_answers = []
    qa = []

    # debug
    aaa = 0

    while "Screen capturing":
        aaa += 1
        sct_img = sct.grab(scope)
        img = np.ascontiguousarray(numpy.array(sct_img)[:, :, 0:3])
        print("current state: ", state)

        id_topups = match(img, templates["topup"])
        if len(id_topups) > 0:
            lerp_iter(mouse, id_topups[0], 1)
            time.sleep(0.5)
            mouse.press(Button.left)
            mouse.release(Button.left)
            time.sleep(0.5)
            continue

        if state == "init":
            id_negos = match(img, templates["nego"])
            if len(id_negos) > 0:
                lerp_iter(mouse, id_negos[0], 1)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                state = "prepare_question"
                continue

        elif state == "prepare_question":
            sct.shot(output=str(aaa) + "question.png")
            id_chooses = match(img, templates["choose"])
            if len(id_chooses) > 0:
                lerp_iter(mouse, id_chooses[0], 1)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                mouse.position = (50, 550)
                questions = id_chooses
                state = "prepare_answer"
                continue

        elif state == "prepare_answer":
            sct.shot(output=str(aaa) + "answer.png")
            id_answers = match(img, templates["answer"])
            if len(id_answers) > 0:
                answers = id_answers
                for i in range(len(questions)):
                    possible_answers.append([i for i in range(len(id_answers))])
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                state = "play"
                continue

        elif state == "play":
            questions.sort(key=lambda x: x[0])
            answer_ids = [i for i in range(len(answers))]
            random.shuffle(answer_ids)
            print("shuffle answer", answer_ids)
            ans = answer_ids * 5
            print("selected answer", ans)
            qa = []

            for i in range(len(questions)):
                pos_answers = possible_answers[i]
                print("pos answer", pos_answers)
                if pos_answers == []:
                    qa.append(None)
                    continue

                # click question
                lerp_iter(mouse, questions[i], 1)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)

                choose_ans = ans[i]
                choose_id = i
                for j in range(choose_id, len(ans)):
                    if ans[j] in pos_answers:
                        choose_ans = ans[j]
                        choose_id = j
                        break

                for j in range(choose_id, len(ans)):
                    if ans[j] not in qa and ans[j] in pos_answers:
                        choose_ans = ans[j]
                        choose_id = j
                        break

                print("choose answer", choose_ans)
                # click answer
                lerp_iter(mouse, answers[choose_ans], 1)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                mouse.position = (50, 550)
                qa.append(choose_ans)
            state = "send"
            continue

        elif state == "send":
            id_send = match(img, templates["send"])
            if len(id_send) > 0:
                mouse.position = add_offset(id_send[0], 0, -50)
                time.sleep(0.5)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(0.5)
                state = "update_possible_answers"
                continue

        elif state == "update_possible_answers":
            sct.shot(output=str(aaa) + "update.png")
            id_corrects = [(*xy, "correct") for xy in match(img, templates["correct"])]
            id_incorrects = [(*xy, "incorrect") for xy in match(img, templates["incorrect"])]
            id_wrong_persons = [(*xy, "wrong-person") for xy in match(img, templates["wrong-person"])]
            results = id_corrects + id_incorrects + id_wrong_persons
            results.sort(key=lambda x: x[0])
            if len(id_corrects) + len(id_incorrects) + len(id_wrong_persons) >= 5:
                wrong_answer_ids = []
                for i in range(len(results)):
                    (x, y, status) = results[i]
                    if status == "correct":
                        print("correct")
                        possible_answers[i] = []
                    elif status == "incorrect":
                        print("incorrect")
                        answered_id = qa[i]
                        for possible_answer in possible_answers:
                            if answered_id in possible_answer:
                                possible_answer.remove(answered_id)
                    else:
                        print("wrong person")
                        answered_id = qa[i]
                        wrong_answer_ids.append(answered_id)
                        if answered_id in possible_answers[i]:
                            possible_answers[i].remove(answered_id)
                    print(i, "possible answer", possible_answers)
                print("qa", qa)
                print("wrong_answer_ids", wrong_answer_ids)
                print("possible answer", possible_answers)

                remaining_count = len(possible_answers) - possible_answers.count([])
                if remaining_count == len(wrong_answer_ids):
                    for possible_answer in possible_answers:
                        temp = []
                        for a in possible_answer:
                            if a in wrong_answer_ids:
                                temp.append(a)
                        print("temp", temp)
                        possible_answer = temp
                state = "play"
                continue
            else:
                time.sleep(0.5)
