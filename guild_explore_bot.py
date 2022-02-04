import time
import cv2
import numpy as np
import mss
import numpy
import random
from pynput.mouse import Button, Controller
import keyboard

templates = {
    # "arrow": cv2.imread("nego/arrow.png"),
    "arrow": cv2.imread("nego/arrow2.png"),
    "get-reward": cv2.imread("nego/get-reward.png"),
    "nego": cv2.imread("nego/start.png"),
    "nego2": cv2.imread("nego/start2.png"),
    "choose": cv2.imread("nego/choose.png"),
    "answer": cv2.imread("nego/answer2.png"),
    "send": cv2.imread("nego/send.png"),
    "correct-sign": cv2.imread("nego/correct-sign.png"),
    "correct": cv2.imread("nego/correct.png"),
    "incorrect": cv2.imread("nego/incorrect.png"),
    "wrong-person": cv2.imread("nego/wrong-person.png"),
    "topup": cv2.imread("nego/topup.png"),
    "success": cv2.imread("nego/success.png"),
    "check-incompleted": cv2.imread("nego/check-incompleted.png"),
    "buy-attempt": cv2.imread("nego/buy-attempt.png"),
    "medal": cv2.imread("nego/medal.png"),
    "next-chapter": cv2.imread("nego/next-chapter.png"),
    "cancel": cv2.imread("nego/cancel.png"),
    "show-answer": cv2.imread("nego/show-answer.png"),
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


def get_scope(state):
    # if state == "init":
    #     return {"top": 0, "left": 0, "width": 1700, "height": 1000}
    # else:
    return {"top": 360, "left": 480, "width": 1330 - 480, "height": 930 - 360}


def click_at(pos, state, mouse):
    offset = get_scope(state)
    lerp_iter(mouse, add_offset(pos, offset["left"], offset["top"]), 1)
    time.sleep(0.1)
    mouse.press(Button.left)
    time.sleep(0.2)
    mouse.release(Button.left)
    time.sleep(0.1)


def write_by_num(num):
    keyboard.write(str(num))


def exit_and_start(pos, mouse):
    time.sleep(0.5)
    for _ in range(10):
        keyboard.press_and_release("esc")
        time.sleep(0.2)

    click_at(pos, "init", mouse)


with mss.mss() as sct:
    state = "init"
    mouse = Controller()
    questions = None
    answers = None
    possible_answers = []
    qa = []
    ref_pos = (1000, 623)
    start_pos = (ref_pos[0] - 480, ref_pos[1] - 360)  # minus offset

    # debug
    aaa = 0

    while "Screen capturing":
        aaa += 1
        sct_img = sct.grab(get_scope(state))
        img = np.ascontiguousarray(numpy.array(sct_img)[:, :, 0:3])
        print("current state: ", state)

        test_nego = match(img, templates["nego"])
        if len(test_nego) > 0 and state != "init":
            state = "init"

        if state == "init":
            # sct.shot(output=str(aaa) + "init.png")
            # 1. clear state
            questions = None
            answers = None
            possible_answers = []
            qa = []

            # 2 find nego button (batlle ground)
            id_negos = match(img, templates["nego"])
            if len(id_negos) > 0:
                click_at(id_negos[0], state, mouse)
                mouse.position = (50, 400)
                state = "prepare_question"
                continue

            # 5. find get reward
            id_rewards = match(img, templates["get-reward"])
            if len(id_rewards) > 0:
                click_at(add_offset(id_rewards[0], 0, -15), state, mouse)
                mouse.position = (50, 400)
                continue

        elif state == "prepare_question":
            # sct.shot(output=str(aaa) + "question.png")
            id_chooses = match(img, templates["choose"])
            if len(id_chooses) > 0:
                # click_at(id_chooses[0], state, mouse)
                write_by_num(1)
                questions = [i for i in range(len(id_chooses))]
                state = "prepare_answer"
                continue

        elif state == "prepare_answer":
            # sct.shot(output=str(aaa) + "answer.png")
            id_answers = match(img, templates["answer"])
            if len(id_answers) > 0:
                answers = [i for i in range(len(id_answers))]
                for i in range(len(questions)):
                    possible_answers.append([i for i in range(len(id_answers))])
                # click_at(mouse.position, state, mouse)
                keyboard.press_and_release("esc")
                time.sleep(0.5)
                state = "play"
                continue

        elif state == "play":
            # sct.shot(output=str(aaa) + "play.png")
            if len(qa) == len(questions):
                for i in range(len(qa)):
                    if qa[i] is not None:
                        # click_at(questions[i], state, mouse)
                        # click_at(answers[qa[i]], state, mouse)
                        write_by_num(questions[i] + 1)
                        time.sleep(0.2)
                        write_by_num(answers[qa[i]] + 1)
                        time.sleep(0.2)

            else:
                questions.sort()
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
                    # click_at(questions[i], state, mouse)
                    print("write q", questions[i] + 1)
                    write_by_num(questions[i] + 1)
                    time.sleep(0.2)

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
                    # click_at(answers[choose_ans], state, mouse)
                    print("write a", answers[choose_ans] + 1)
                    write_by_num(answers[choose_ans] + 1)
                    qa.append(choose_ans)
                    time.sleep(0.2)

            state = "send"
            continue

        elif state == "send":
            id_send = match(img, templates["send"])
            if len(id_send) > 0:
                print("found send")
                # click_at(add_offset(id_send[0], 0, -50), state, mouse)
                keyboard.press_and_release("space")
                state = "checking_and_update"
                continue

            id_topups = match(img, templates["topup"])
            if len(id_topups) > 0:
                print("found topup")
                click_at(add_offset(id_topups[0], 0, -15), state, mouse)
                time.sleep(0.5)
                mouse.position = (50, 400)
                state = "play"
                continue

            # cancel case
            # id_cancels = match(img, templates["cancel"])
            # if len(id_cancels) > 0:
            #     print("found cancel")
            #     click_at(add_offset(id_cancels[0], 0, -15), state, mouse)
            #     time.sleep(1)
            #     click_at(add_offset(id_cancels[0], 40, -25), state, mouse)
            #     state = "play"
            #     continue

            # The answer still has showed because it clicked too fast.
            id_show_answers = match(img, templates["show-answer"])
            if len(id_show_answers) > 0:
                print("found show answer")
                state = "play"
                continue

            # can't play, then replay
            id_check_incompleted = match(img, templates["check-incompleted"])
            id_chooses = match(img, templates["choose"])
            if len(id_chooses) > 0 or len(id_check_incompleted):
                print("found incompleted")
                time.sleep(0.2)
                state = "play"
                continue

        elif state == "checking_and_update":
            # sct.shot(output=str(aaa) + "pending_update.png")

            # The answer still has showed because it clicked too fast.
            id_show_answers = match(img, templates["show-answer"])
            if len(id_show_answers) > 0:
                print("found show answer")
                state = "play"
                continue

            #  Out of round, then top up
            id_topups = match(img, templates["topup"])
            if len(id_topups) > 0:
                click_at(id_topups[0], state, mouse)
                continue

            # case1: if correct sign + choose sign >= 5, then update the possible answer
            id_chooses = match(img, templates["choose"])
            id_correct_signs = match(img, templates["correct-sign"])
            if (len(id_chooses) + len(id_correct_signs) >= 5) and len(id_correct_signs) < 5:
                # update state
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
                    if remaining_count == len(set(wrong_answer_ids)):
                        for i in range(len(possible_answers)):
                            temp = []
                            for a in possible_answers[i]:
                                if a in wrong_answer_ids:
                                    temp.append(a)
                            print("temp", temp)
                            possible_answers[i] = temp
                    print("possible answer2", possible_answers)
                    qa = []
                    state = "play"
                    continue
                else:
                    print("can't update")

            # case2: if correct sign >= 5 or found success, it means the stage is completed.
            id_success = match(img, templates["success"])
            if len(id_correct_signs) >= 5 or len(id_success) > 0:
                time.sleep(0.5)
                exit_and_start(start_pos, mouse)
                state = "init"
                continue
