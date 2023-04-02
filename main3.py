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


    def handMovement(move):
        if move==1:
            servo.angle = -25 
        else:
            servo.angle = -90
        return    

    def addFace(img, name):
        encodes, name = [], name
        faceLoc = fr.face_locations(img)
        if len(faceLoc) == 1:
            faceEnc = fr.face_encodings(img)[0]
            encodes.append(list(faceEnc.flatten()))
        return encodes, name
   
    def addFaceData(encodes, name):
            
        with open("faceEncodesNew.json", 'r+') as f:
            faceData = json.load(f)
            faceData['faces'].append({'name': name, 'faceEncodes': encodes})
            faceData['names'].append(name)
            f.seek(0)
            json.dump(faceData, f, indent=4)


    def captureImageTrain(name):
    
        cap = cv2.VideoCapture(0)
        while True:
            _, img = cap.read()
            if _:
                cv2.imshow("Train Image Capture", img)
                k = cv2.waitKey(1)
                if k == 27:
                    break
                elif k == 32:
                    encodes, name = addFace(img, name)
                    addFaceData(encodes, name)
                    return True

    def getEncodes():
        
        names, encodes = [], []
        with open('./faceEncodesNew.json', 'r') as f:
            faceData = json.load(f)
        for i in faceData['faces']:
            encodes.append(i['faceEncodes'][0])
            names.append(i['name'])
        return encodes, names

    def findFace(img):
        global guestCount
        faceLoc = fr.face_locations(img)
        facesPresent = []
        knownEncodes, names = getEncodes()
        faceEnc = fr.face_encodings(img)
        print(np.array(knownEncodes).shape)

        for i in range(len(faceEnc)):    
            enc = faceEnc[i]
            faceDistance = fr.face_distance(knownEncodes, enc)
            if np.argmax(faceDistance) > 0.5:
                nameIndex = names[np.argmax(faceDistance)]
                facesPresent.append(nameIndex)
            else:
                facesPresent.append(f"Guest{guestCount}")
                guestCount += 1
        return facesPresent

    def speechNameOutput(names):
        greet = "Welcome to the A I M L Lab"
        print(names)
        if len(names):
            handMovement(1)
        for name in names:
            engine.say(greet)
            if "Guest" in name:
                name = "Guest"
            speechOutput(f"{name} Please give HandShake")
            if temperatureCheck():
                speechOutput("Your Temperature is Normal, walk in")
            else:
                speechOutput("Your Temperature is abnormal please wait")
                print('Done')
            engine.runAndWait()
        if len(names):
            handMovement(0)
       


    def speechOutput(msg):
       
        engine.say(msg)
        engine.runAndWait()

    def findFaceCam():
        global detectionStack
        cap = cv2.VideoCapture(0)
        frameCountClean = 1
        frameCount = 1
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
                speechNameOutput(names)
                frameCountClean+=1
            if frameCountClean == 150:
                detectionStack = []
            frameCount += 1     

    def temperatureCheck() -> bool:
        # TEMPERATURE
        bus = SMBus(1)
        sensor = MLX90614(bus, address=0x5A)
        l = []
        while 1:
            x = sensor.get_obj_temp() - 10
            if x > 24:
                l.append(x)
            if len(l) == 300:
                break
        if 23 < max(l) <= 40:
            return True
        else:
            return False

   

    if __name__ == "__main__":
       
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1)
    
        servo = AngularServo(18, min_pulse_width=0.0006, max_pulse_width=0.0023)
        servo.angle = -90
       
        # Global Variables
        detectionStack = []
       
        speechOutput("hi am you amino")
        findFaceCam()
        # if captureImageTrain("Mister Sai Krishna"):
        #     print("Completed")
   
           
except:
    pass 