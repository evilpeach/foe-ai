import cv2
import numpy as np

img_rgb = cv2.imread('r_page_2.png')
templates = [
    cv2.imread('template_r_1.png'),
]
colors = [(0, 0, 255)]

for i in range(len(templates)):
    w, h = templates[i].shape[:-1]
    res = cv2.matchTemplate(img_rgb, templates[i], cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), colors[i], 2)

cv2.imwrite('result_r2.png', img_rgb)
