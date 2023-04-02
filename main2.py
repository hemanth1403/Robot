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
       
        global newFaceAdded
       
        with open("faceEncodes.json", 'r+') as f:
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
                elif k == 32:
                    imgArray.append(img)
        print(len(imgArray), imgArray[0].shape)
        encodes, name = addFace(imgArray, name)
        addFaceData(encodes, name)

    def getEncodes():
       
        names, encodes = [], []
        with open('./faceEncodes.json', 'r') as f:
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
        clf = svm.SVC(gamma='scale')
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
            name = clf.predict([enc])
            facesPresent.append(name[0])
       
        return facesPresent

    def speechNameOutput(names):
        greet = "Welcome to the A I M L Lab"
        print(names)
        if len(names):
            handMovement(1)
        for name in names:
            engine.say(greet)
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
        #factory = PiGPIOFactory()
        servo = AngularServo(18, min_pulse_width=0.0006, max_pulse_width=0.0023)
        servo.angle = -90
        #servo = Servo(18, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
        # MOTOR MOVEMENT
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setwarnings(False)
        #Ena,In1,In2=31,17,27
        #GPIO.setup(Ena,GPIO.OUT)
        #GPIO.setup(In1,GPIO.OUT)
        #GPIO.setup(In2,GPIO.OUT)
        #pwm=GPIO.PWM(Ena,100)
        #pwm.start(0)
        #GPIO.output(In1,GPIO.LOW)
        #GPIO.output(In2,GPIO.LOW)
       
       
       
       
        # Global Variables
        clf = None
        detectionStack = []
        newFaceAdded = False
       
        speechOutput("hi am you amino")
        findFaceCam()
        # addTrainData("Tom Bhaaya", "./Images/")
   
           
except:
    pass 
