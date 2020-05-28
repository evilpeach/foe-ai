import cv2
import numpy as np

img_rgb = cv2.imread('base2.png')
templates = [
    cv2.imread('template1.png'),
    cv2.imread('template2.png'),
    cv2.imread('template3.png'),
    cv2.imread('template4.png'),
    cv2.imread('template5.png'),
]
colors = [(0, 0, 255), (0, 255, 0), (255, 0,  0), (255, 0, 255), (255, 255, 0)]

for i in range(len(templates)):
    w, h = templates[i].shape[:-1]
    res = cv2.matchTemplate(img_rgb, templates[i], cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), colors[i], 2)

cv2.imwrite('result.png', img_rgb)
