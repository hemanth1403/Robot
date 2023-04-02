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
        for name in names:
            engine.say(greet)
            speechOutput(f"{name} Please give HandShake")
            if temperatureCheck():
                speechOutput("Your Temperature is 5n, walk in")
            else:
                speechOutput("Your Temperature is abnormal please wait")
                print('Done')
            engine.runAndWait()
        


    def speechOutput(msg):
        
        engine.say(msg)
        engine.runAndWait()

    def findFaceCam():
        
        global detectionStack


        cap = cv2.VideoCapture(0)
        frameCount = 1
        frameCountClean = 1
        while True:
            
            _, img = cap.read()
            if _ and frameCount%5==0:
                
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
            
            
            
    def handMovement(move):
        if move == 1:
            x=1
            while x<=1000000:
                GPIO.output(In1,GPIO.LOW)
                GPIO.output(In2,GPIO.HIGH)
                pwm.ChangeDutyCycle(100)
                x+=1
                
        else:
            x = 1
            while x<=1000000:
                GPIO.output(In1,GPIO.HIGH)
                GPIO.output(In2,GPIO.LOW)
                pwm.ChangeDutyCycle(100)
                x+=1
            



    def temperatureCheck():
        
        # TEMPERATURE
        bus = SMBus(1)
        sensor = MLX90614(bus, address=0x5A)
        while 1:
            x=int(sensor.get_obj_temp())
            x-=14
            l=[]
            sett=0
            while x>=24:
                x=int(sensor.get_obj_temp())
                x-=14
                print(x, len(l))
                l.append(x)
                
                if len(l)>=100:
                    sett=1
                    break
            if sett==1:
                break
        bus.close()
        
        if max(l)>=24 and max(l)<=40:
            return True
        return False
            

    

    if __name__ == "__main__":
        
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        
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
        #
        detectionStack = []
        newFaceAdded = False
        
        findFaceCam()
        # addTrainData("Tom Bhaaya", "./Images/")
    
            
except:
    pass
    
