import time
import cv2
import numpy as np
import mss
import numpy

templates = [
    cv2.imread('idle/t_box.png'),
    cv2.imread('idle/t_close.png'),
    cv2.imread('idle/t_coin.png'),
    cv2.imread('idle/t_resource.png'),
    cv2.imread('idle/t_sleep.png'),
    cv2.imread('idle/t_sword.png'),
]
colors = [(0, 0, 255), (0, 255, 255), (0, 255, 0),
          (255, 0,  0), (255, 0, 255), (255, 255, 0)]


with mss.mss() as sct:
    # Part of the screen to capture
    monitor = {"top": 100, "left": 0, "width": 950, "height": 735}

    while "Screen capturing":
        last_time = time.time()

        # Get raw pixels from the screen, save it to a Numpy array
        sct_img = sct.grab(monitor)
        img = np.ascontiguousarray(numpy.array(sct_img)[:, :, 0:3])

        for i in range(len(templates)):
            w, h = templates[i].shape[:-1]
            res = cv2.matchTemplate(
                img, templates[i], cv2.TM_CCOEFF_NORMED)
            threshold = .8
            loc = np.where(res >= threshold)
            for pt in zip(*loc[::-1]):  # Switch collumns and rows
                cv2.rectangle(
                    (img), pt, (pt[0] + w, pt[1] + h), colors[i], 4)
            # print([pt for pt in zip(*loc[::-1])])

        resized = cv2.resize(img, (950//2, 735//2),
                             interpolation=cv2.INTER_AREA)

        cv2.imshow("Resized image", resized)

        print("fps: {}".format(1 / (time.time() - last_time)), end='\r', flush=True)

        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break
