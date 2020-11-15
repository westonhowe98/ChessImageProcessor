import os
import cv2
import numpy as np
import pandas as pd
from ChessBotSettings import *


Templates = {}

PixelSignatures = {}

def TemplatesExist():
    return not (os.path.isfile(SignatureFile) and os.path.getsize(SignatureFile) > 0)

def LoadTemplates():
    global Templates
    print("Loading Templates")

    Filenames = []
    for Color in Colors:
        for PieceType in PieceTypes:
            Filename = PieceImageDir + Color + PieceType + ".png"
            Filenames.append(Filename)

    Filenames.append(PieceImageDir + "BlankSquare" + ".png")

    for Filename in Filenames:
        template = cv2.imread(Filename)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        SimplifyImage(template)

        Templates[Filename] = template

def EvaluatePixel(PixelCandidate, x, y):
    global Templates
    global PixelSignatures

    Matches = []
    for Filename, Template in Templates.items():
        EvalPixel = Template[y, x]
        if EvalPixel == PixelCandidate: # are exactly the same color
            Matches.append(Filename)

    return len(Matches)

def GetSignature(Filename):
    EvalTemplate = Templates[Filename]

    for x in range(SquareSize):
        for y in range(SquareSize):
            EvalPixel = EvalTemplate[y, x]
            if EvaluatePixel(EvalPixel, x, y) == 1:
                return x, y

    return None

def GenerateSignatures():
    if len(Templates) == 0:
        LoadTemplates()

    global PixelSignatures

    print("Generating Pixel Signatures")

    for Filename in Templates.keys():
        Signature = GetSignature(Filename)
        if Signature != None:
            PixelSignatures[Filename] = Signature
        else:
            print("Signature not found for: ", Filename)

    SaveSignatures()

def DisplaySignatures():
    if len(Templates) == 0:
        LoadTemplates()

    for Filename, Signature in PixelSignatures.items():
        x, y = Signature
        Pixel = Templates[Filename][y, x]

        print(Filename, Signature, Pixel)

def LoadSignatures():

    global PixelSignatures

    File = open(SignatureFile, 'r')

    for Line in File:
        Values = Line.split(',')
        Filename = Values[0]
        x = int(Values[1])
        y = int(Values[2])

        Signature = (x, y)

        PixelSignatures[Filename] = Signature

    File.close()
    DisplaySignatures()

def SaveSignatures():
    OutputFile = open(SignatureFile, 'w')
    for Filename, Signature in PixelSignatures.items():
        x, y = Signature

        Line = ""
        Line += str(Filename)
        Line += ','
        Line += str(x)
        Line += ','
        Line += str(y)
        Line += '\n'

        OutputFile.write(Line)
    OutputFile.close()

def SimplifyTemplates():
    for Filename, Template in Templates.items():
        SimplifyImage(Template)
        SimpleFilename = Filename.split('/')[1]
        cv2.imwrite("TestImgs/" + SimpleFilename, Template)

def SimplifyImage(Img):
    Img[Img != 0] = 255