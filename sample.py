import face_recognition as fr
import cv2
import numpy



def addFace(imgArray, name):
    
    encodes, name = [], name
    for person in imgArray:
        faceLoc = fr.face_locations(person)
        if len(faceLoc) == 1:
            faceEnc = fr.face_encodings(person)[0]
            encodes.append(list(faceEnc.flatten()))
    return encodes, name

