from numpy import rint

try:
    import face_recognition as fr
    import cv2
    from sklearn import svm
    import json
    import pyttsx3
    import RPi.GPIO as GPIO
    from time import sleep
    from smbus2 import SMBus
    from mlx90614 import MLX90614
    from gpiozero import AngularServo,Servo
    import numpy as np
    from subprocess import call
    import os
    import pyttsx3
    import datetime
    from time import sleep

    def voiceRecognition():
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate',130)
        # voices = engine.getProperty('voices')
        q=['Are you excited to know the new and renewed strategy for T-Hub 2.0?','Do you want to know about the founders of t hub', 'do you want to know How does T-Hub impact startups?', 'Do you want to know how many startups has T-Hub impacted? ,, ?', 'Do you want to Connect with T Hub']
        l=['Building on top of the existing strategy, T-Hub 2.0 will bring greater emphasis on funding and policy support for startups. ','T Hub core founding partners are the Government of Telangana, triple i T Hyderabad, Indian School of Business and Nalsar University', 'T-Hub has accelerated the journey of various startups through a diverse set of programmes, from masterclasses for idea stage to T-Angel for making startups investor ready. Moreover, T-Hub facilitates the connections between startups and investors, corporations, government, academia and more. ','To this day, T-Hub has impacted 1100+ national and international startups through varied engagements. ', "To know more about T-Hub's programmes and collaborations, you may visit www.t-hub.co  and fill the contact form. "]
        c=0
        try:
            # f = 0 
            while c<len(q):
                engine.say(q[c])
                engine.runAndWait()
                # audio = r.listen(source)
                # query = r.recognize_google(audio,language='en-in').lower()
                x = int(input("Query : "))
                # print(f"User said: {query}\n")
                if(x==1):
                    # f = 0
                    engine.say(l[c])
                    engine.runAndWait()   
                    c+=1
                elif(x == 0):
                    # f = 1
                    break
            engine.say("Thank you ,,, Have a nice Day")
            engine.runAndWait()
        except:
            pass

    def handMovement(move):
        if move==1:
            servo.angle = -25 
        else:
            servo.angle = -90
        return    

    def addFace(imgArray, name):
       
        encodes, name = [], name
        for person in imgArray:
            faceLoc = fr.face_locations(person)
            if len(faceLoc) == 1:
                faceEnc = fr.face_encodings(person)[0]
                encodes.append(list(faceEnc.flatten()))
        return encodes, name
    
    def addTrainData(name, path = './Images/'):
        global newFaceAdded

        imgArray = []
        for img in os.listdir(path):
            imgArray.append(cv2.imread(path + img))
        encodes, name = addFace(imgArray, name)
        addFaceData(encodes, name)
   

    def addFaceData(encodes, name):
        with open("faceEncodes.json", 'r+') as f:
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
                for i in range(3):
                    k = int(input())
                    if k == 0:
                        break
                    elif k == 1:
                        imgArray.append(img)
                if i == 2:
                    break
        print(len(imgArray), imgArray[0].shape)
        encodes, name = addFace(imgArray, name)
        addFaceData(encodes, name)

    def getEncodes():
        
        names, encodes = [], []
        with open('./faceEncodes1.json', 'r') as f:
            faceData = json.load(f)
        for i in faceData['faces']:
            encodes.extend(i['faceEncodes'])
            names.extend([i['name']]*len(i['faceEncodes']))
        return encodes, names

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
                if guestCount % 3 == 0:
                    facesPresent.append(f"Guest{guestCount}")
                guestCount += 1
            else:
                nameIndex = knownNames[faceDistance.index(min(faceDistance))]
                facesPresent.append(nameIndex)
        return facesPresent

    def speechNameOutput(names):
        greet = "Welcome to AIERC LAB"
        print(names)
        if len(names) != 0:
            handMovement(1)
        for name in names:
            engine.say(greet)
            if "Guest" in name:
                name = "Guest"
            speechOutput(f"{name} Please give HandShake")
            # if 1:
            #     speechOutput('Let me tell you about t hub')
            #     x = input("Enter Handdown: ")
            #     servo.angle = -90
            #     speechOutput('T-Hub stands for Technology Hub, which was incorporated in 2015, It is India’s pioneering innovation ecosystem that enables the acceleration of startups, facilitates corporations, open innovation endeavours and brings together various stakeholders from investors, government and more to catalyse the flame of entrepreneurship. ')
            #     voiceRecognition()
            # else:
            #     speechOutput('Let me tell you about t hub')
            #     x = input("Enter Handdown: ")
            #     servo.angle = -90
            #     speechOutput('T-Hub stands for Technology Hub, which was incorporated in 2015, It is India’s pioneering innovation ecosystem that enables the acceleration of startups, facilitates corporations, open innovation endeavours and brings together various stakeholders from investors, government and more to catalyse the flame of entrepreneurship. ')
            #     voiceRecognition()
            x = int(input("Enter for Temp (1 - Normal) or (0 - Abnormal):"))
            if(x ==1):
                speechOutput("Your temperature is Normal, please Walk In")
                y = input("Enter to handDown: ")
                servo.angle = -90
            else:
                speechOutput("Your temperature is Abnormal, please consider having a check up")
                y = input("Enter to handDown: ")
                servo.angle = -90

            engine.runAndWait()
        if len(names):
            handMovement(0)
       


    def speechOutput(msg):
       
        engine.say(msg)
        engine.runAndWait()
    
    def speechOutputEspeak(msg):
        cmd_beg = 'espeak '
        call([f'{cmd_beg} "{msg}"'], shell=True)

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
                speechNameOutput(sorted(names, reverse=True))
                frameCountClean+=1
            if frameCountClean == 150:
                detectionStack = []
            frameCount += 1


    def enhance(img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_img_eqhist = cv2.equalizeHist(gray_img)
        clahe = cv2.createCLAHE(clipLimit=40)
        gray_img_clahe = clahe.apply(gray_img_eqhist)
        return cv2.cvtColor(gray_img_clahe, cv2.COLOR_GRAY2BGR)

    def temperatureCheck() -> bool:
        # TEMPERATURE
        bus = SMBus(1)
        sensor = MLX90614(bus, address=0x5A)
        l = []
        while 1:
            x = sensor.get_obj_temp() - 10
            if x > 22:
                l.append(x)
            if len(l) == 300:
                break
        if 25 < max(l) <= 40:
            return True
        else:
            return False

   

    if __name__ == "__main__":
       
        engine = pyttsx3.init()
        engine.setProperty("rate", 130)
        engine.setProperty("volume", 1)
    
        servo = AngularServo(18, min_pulse_width=0.0006, max_pulse_width=0.0023)
        servo.angle = -90
       
        # Global Variables
        detectionStack = []
        guestCount = 0
        knownEncodes, knownNames = getEncodes()
        # print(knownEncodes, names)
        speechOutput("Hi I am Amino")
        print("Started")
        x = int(input("Enter 1 to train or 2 to detect : "))
        if x == 1:
            captureImageTrain(input("Enter name: "))
            print("Completed")
        elif x == 2:
            findFaceCam()
   
           
except Exception as e:
    print(e)
