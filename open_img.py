import matplotlib.pyplot as plt
import matplotlib

import cv2
import numpy as np

matplotlib.use('TkAgg')

img = cv2.imread('test.png')

# selection = img[1953:1993, 460:618]
# mean_color = np.mean(selection, axis=(0, 1))
# print(mean_color)

imgplot = plt.imshow(img)

plt.show()
