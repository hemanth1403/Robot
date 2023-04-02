import cv2
cap = cv2.VideoCapture(0)

while True:
    _, img = cap.read()
    cv2.imshow("Imagwe", img)
    k = cv2.waitKey(1)
    if k == 32:
        break
    