import os
from random import randint
from imageai.Detection import ObjectDetection
import cv2
import numpy as np


#images = os.listdir('data/')
model_path = os.path.join(os.curdir, 'yolo-tiny.h5')

detector = ObjectDetection()
detector.setModelTypeAsTinyYOLOv3()
detector.setModelPath(model_path)
detector.loadModel(detection_speed="normal")
custom = detector.CustomObjects(car=True, motorcycle=True, bus=True, truck=True, suitcase=True)

cam_url = "http://138.97.200.115/mjpg/video.mjpg?camera=1"

cap = cv2.VideoCapture(cam_url)

# Check if camera opened successfully
if (cap.isOpened() == False):
  print("No se pudo abrir la camara, revise la url de la cámara")

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
print("Empezando a leer video...")

i=0
while(True):
    ret, frame = cap.read()

    if ret == True:
        k = cv2.waitKey(1)
        # Press Q on keyboard to stop recording
        if k == ord('q'):
            print("Bye")
            break
    
        frame = cv2.pyrDown(frame)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        out_frame, detection = detector.detectCustomObjectsFromImage(custom_objects = custom,
                                                                    input_type="array",
                                                                    input_image=frame,
                                                                    output_type="array")
        
        if detection: 
            #print(detection)
            #print(type(detection))
            box_points = detection[0]["box_points"]
            x = box_points[0]
            y = box_points[1]
            xw = box_points[2]
            yh = box_points[3]
            auto = frame[y:yh, x:xw]
            #frame = cv2.rectangle(frame, start_point, end_point, (125, 125, 0), 2)
            cv2.imwrite("auto{}.jpg".format(i), auto) 
            i += 1

        cv2.imshow('IP Publica', frame)
        cv2.imshow('Deteccion', out_frame)

    # Break the loop
    else:
        break

cap.release()
""" 
for image in images:
    input_path = os.path.join(os.curdir, 'data', image)
    output_path = os.path.join(os.curdir, 'output', image)
    for eachItem in detection:
        if eachItem["name"] in ('car', 'truck', 'suitcase', 'motorcycle'):
            print(eachItem["name"] , " : ", eachItem["percentage_probability"]) """