from base64 import encode
import face_recognition as fr
import cv2
import json
import numpy as np
import os



def addFace(imgArray, name):
    # print(imgArray)
    encodes, name = [], name
    for img in imgArray:
        faceLoc = fr.face_locations(img)
        if len(faceLoc) == 1:
            faceEnc = fr.face_encodings(img)[0]
            encodes.append(list(faceEnc.flatten()))
    # print(encodes,name)
    return encodes, name


def getEncodes():
        
    names, encodes = [], []
    with open('./faceEncodes1.json', 'r') as f:
        faceData = json.load(f)
    for i in faceData['faces']:
        encodes.extend(i['faceEncodes'])
        names.extend([i['name']]*len(i['faceEncodes']))
    return encodes, names

def addFaceData(encodes, name):
           
    with open("./faceEncodes1.json", 'r+') as f:
        faceData = json.load(f)
        faceData['faces'].append({'name': name, 'faceEncodes': encodes})
        faceData['names'].append(name)
        f.seek(0)
        json.dump(faceData, f, indent=4)

def captureImageTrain(name):
    cap = cv2.VideoCapture(0)
    imgArray = []
    while True:
        _, img = cap.read()
        if _:
            cv2.imshow("Train Image Capture", img)
            k = cv2.waitKey(1)
            if k == 27:
                break
            elif k == 32:
                imgArray.append(img)
                if len(imgArray) == 3:
                    break
            encodes, name = addFace(img, name)
            addFaceData(encodes, name)
            return True

def findFace(img):
    global guestCount
    global knownEncodes, knownNames
    faceLoc = fr.face_locations(img)
    facesPresent = []
    faceEnc = fr.face_encodings(img, faceLoc) 
    for i in range(len(faceEnc)):  
        enc = faceEnc[i]
        faceDistance = list(fr.face_distance(knownEncodes, enc))
        # print(faceDistance)
        if min(faceDistance) > 0.5:
            if guestCount % 5 == 0:
                facesPresent.append(f"Guest{guestCount}")
            guestCount += 1
        else:
            nameIndex = knownNames[faceDistance.index(min(faceDistance))]
            facesPresent.append(nameIndex)
    return facesPresent

def addTrainData(name, path = './Images/'):
    global newFaceAdded

    imgArray = []
    for img in os.listdir(path):
        imgArray.append(cv2.imread(path + img))
    encodes, name = addFace(imgArray, name)
    addFaceData(encodes, name)

def findFaceCam():
    global detectionStack
    cap = cv2.VideoCapture(0)
    frameCountClean = 1
    frameCount = 1
    while True:
        t, img = cap.read()
        if t and frameCount % 5 == 0:
            faces = findFace(img)
            names = []
            for i in faces:
                
                if i in detectionStack:
                    continue
                else:
                    names.append(i)
                    detectionStack.append(i)

            print(detectionStack, names)
            frameCountClean+=1
        if frameCountClean == 50:
            detectionStack = []
        frameCount += 1    


if __name__ == "__main__":

    detectionStack = []
    guestCount = 0
    knownEncodes, knownNames = getEncodes()
    # print(knownEncodes, names)

    print("Started")
    # if ("Mister Jayesh Ranjan"):
    #     print("Completed")
    # addTrainData("Mister Jayesh Ranjan")
    # print("Completed")
    # print(knownNames)
    findFaceCam()
