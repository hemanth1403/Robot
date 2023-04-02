import face_recognition as fr
import cv2
from sklearn import svm
import json
import pyttsx3
import os



def addFace(imgArray, name):
    encodes, name = [], name
    for person in imgArray:
        faceLoc = fr.face_locations(person)
        if len(faceLoc) == 1:
            faceEnc = fr.face_encodings(person)[0]
            encodes.append(list(faceEnc.flatten()))
    return encodes, name

def addFaceData(encodes, name):
    global newFaceAdded
    
    with open("faceEncodes1.json", 'r+') as f:
        faceData = json.load(f)
        faceData['faces'].append({'name': name, 'faceEncodes': encodes})
        faceData['names'].append(name)
        f.seek(0)
        json.dump(faceData, f, indent=4)
    newFaceAdded = True

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
            elif k == 32 and len(imgArray) < 10:
                imgArray.append(img)
            elif len(imgArray) == 10:
                break
    print(len(imgArray), imgArray[0].shape)
    encodes, name = addFace(imgArray, name)
    addFaceData(encodes, name)

def addTrainData(name, path = './Images/'):
    global newFaceAdded

    imgArray = []
    for img in os.listdir(path):
        imgArray.append(cv2.imread(path + img))
    encodes, name = addFace(imgArray, name)
    addFaceData(encodes, name)

def getEncodes():
    names, encodes = [], []
    with open('./faceEncodes1.json', 'r') as f:
        faceData = json.load(f)
    for i in faceData['faces']:
        for j in i['faceEncodes']:
            encodes.append(j)
            names.append(i['name'])
    return names, encodes

def getEncodesReTrainModel():
    global clf
    names, encodes = [], []
    with open('./faceEncodes.json', 'r') as f:
        faceData = json.load(f)
    for i in faceData['faces']:
        for j in i['faceEncodes']:
            encodes.append(j)
            names.append(i['name'])
    clf = svm.SVC(gamma='scale', probability=True)
    clf.fit(encodes, names)


def findFace(img):

    global newFaceAdded, clf

    if newFaceAdded or clf == None:
        getEncodesReTrainModel()
        newFaceAdded = False
    faceLoc = fr.face_locations(img)
    facesPresent = []
    for i in range(len(faceLoc)):
        enc = fr.face_encodings(img)[i]
        # somthing = clf.predict_proba([enc])[0]
        # print(somthing, clf.classes_)
        # if any(map(lambda x:x > (len(clf.classes_)/1000) * 35, clf.predict_proba([enc])[0])):
        name = clf.predict([enc])
        print(name)
        facesPresent.append(name[0])
        # else:
        #     facesPresent.append("Guest")
    return facesPresent

def speechOutput(names):
    greet = "Welcome to the Artificial Intelligence and Machine Learning Lab"
    for name in names:
        engine.say(greet + name)
        engine.runAndWait()

def findFaceCam():
    global detectionStack


    cap = cv2.VideoCapture(0)
    frameCount = 1
    frameCountClean = 1
    while True:
        _, img = cap.read()
        if _ and frameCount % 5 == 0:
            faces = findFace(img)
            names = []
            for i in faces:
                if i in detectionStack:
                    continue
                else:
                    names.append(i)
                    detectionStack.append(i)
                print(detectionStack, names)
            speechOutput(names)
            if "Guest" in detectionStack and frameCountClean % 10 == 0:
                detectionStack.remove("Guest")
            frameCountClean += 1
            
        if frameCountClean == 150:
            detectionStack = []
        frameCount += 1

if __name__ == "__main__":
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    # Global Variables
    clf = None
    detectionStack = []
    newFaceAdded = False

    # captureImageTrain("Mister Phaneendra")
    # print("Started")
    # findFaceCam()
    
    # getEncodesReTrainModel()
    addTrainData("Miss Jyoshna Reddy", "./Images/")
