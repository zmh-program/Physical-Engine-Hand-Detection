import cv2
capture = cv2.VideoCapture(0)
_image = cv2.cvtColor(cv2.flip(capture.read()[1], 1), cv2.COLOR_BGR2RGB)
HEIGHT, WIDTH = _image.shape[:2]
