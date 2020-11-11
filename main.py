import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
import pyautogui
import string
from PIL import Image
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import chess
import stockfish
import random
import sys
import time

FEN_START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

MoveDelay = 0.15
ConfidenceLevel = 0.80

ColorThreadhold = 10

OriginalPieceSize = 60

DarkSquareRGB = (181, 136, 99)
DarkSquareRGBAdj = (209, 174, 137)
LightSquareRGB = (240, 217, 181)

A1 = (621, 854)
SquareSize = 92

#PieceImageDir = "PieceIcons/"
PieceImageDir = "CustomPieceIcons/"

Files = "ABCDEFGH"
Ranks = "12345678"

ClockBackgroundLocation = (1344, 706)
ClockBackgroundColor = (208, 224, 189)

ReplaceColors = [
    DarkSquareRGB,
    (170,162,58),
    (205,210,106)
]

Colors = {"White", "Black"}
PieceTypes = {"King", "Queen", "Rook", "Bishop", "Knight", "Pawn"}

stockfish = stockfish.Stockfish("stockfish_20090216_x64_bmi2.exe", parameters={"Threads": 4, "Minimum Thinking Time": 5, "Hash" : 16})
stockfish.set_skill_level(5)
stockfish.set_depth(8)

UseCorrespondence = True

CurrentFEN = ""
IsWhite = True
DoMove = False

CurrentPieces = {}
CurrentFlippedPieces = {}

Icons = {}
Castles = {}

def main():
    print(stockfish.get_parameters())

    LoadIcons()
    Reset()
    #print(stockfish.get_parameters())
    #print(InvertCoordinate("a1")) # h8
    #print(InvertCoordinate("h8"))  # a1
    Overhead()
    GetBase()
    #DebugCycle()
    Play()
    #DebugPosition()

def Reset():
    global Castles
    Both = (True, True) # King side, queenside
    Castles["White"] = Both
    Castles["Black"] = Both

def GetDelay(Destination):
    return 0.01

    if Destination.upper() in CurrentFlippedPieces:
        return 0

    return random.betavariate(2, 7) * 8

def IsRed(Color):
    r, g, b = Color

    if r > g:
        return True

    if r > b:
        return True

    return False

def LoadIcons():
    global Icons

    for Color in Colors:
        for PieceType in PieceTypes:
            IconFileName = PieceImageDir + Color + PieceType + ".png"
            template = cv2.imread(IconFileName)
            templateG = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            Icons[IconFileName] = templateG

def GetBase():
    global A1
    global IsWhite

    Reset()

    while True:
        A1White = pyautogui.locateCenterOnScreen("A1AsWhite.png")
        H8Black = pyautogui.locateCenterOnScreen("H8AsBlack.png")

        if A1White != None:
            A1 = A1White
            IsWhite = True
            break

        if H8Black != None:
            A1 = H8Black
            IsWhite = False
            break

    print("Is White:", IsWhite)
    print(A1)

def IsMyTurn():
    Timer = pyautogui.locateCenterOnScreen("TimerSource.png")
    if Timer != None:
        x, y = Timer
        if y > (1080/2):
            return True

    Timer2 = pyautogui.locateCenterOnScreen("TimerSource2.png")
    if Timer2 != None:
        x, y = Timer2
        if y > (1080/2):
            GetBase()
            return True

    return False

def WaitForTurn():
    FEN = GetFEN(MapPieces())

    while True:
        if IsMyTurn():
            break

        Pieces = MapPieces()
        NewFEN = GetFEN(Pieces)
        if(NewFEN != FEN):
            break

        Overhead()

def Overhead():
    if pyautogui.locateCenterOnScreen("ClaimVictory.png") != None:
        pyautogui.moveTo(pyautogui.locateCenterOnScreen("ClaimVictory.png"))
        pyautogui.click()
        time.sleep(0.1)
        pyautogui.moveTo(10, 10)

    if pyautogui.locateCenterOnScreen("NewOpponent.png") != None:
        time.sleep(2)
        pyautogui.moveTo(pyautogui.locateCenterOnScreen("NewOpponent.png"))
        pyautogui.click()

        while True:
            if pyautogui.locateCenterOnScreen("A1AsWhite.png") != None:
                break

            if pyautogui.locateCenterOnScreen("H8AsBlack.png") != None:
                break

            GetBase()

def Play():
    #if not IsWhite:
    #    while True:
    #        Pieces = MapPieces()
    #        #print(Pieces)
    ##        FEN = GetFEN(Pieces)
     #       #print(FEN)
     #       if FEN != FEN_START:
     #           break

    while True:
        start = time.time()
        Pieces = MapPieces()
        end = time.time()
        PieceMappingTime = end - start
        #print(Pieces)

        start = time.time()
        FEN = GetFEN(Pieces)
        #print(FEN)
        end = time.time()
        FENGenerationTime = end - start

        start = time.time()
        BestMove = GetBestMove(FEN)
        end = time.time()
        BestMoveTime =  end - start
        #print(BestMove)

        TotalTime = PieceMappingTime + FENGenerationTime + BestMoveTime

        print()
        print("PieceMappingTime: ", PieceMappingTime)
        print("FENGenerationTime: ", FENGenerationTime)
        print("BestMoveTime: ", BestMoveTime)
        print("TotalTime", TotalTime)
        print()

        Move(BestMove)
        WaitForTurn()

def GetBestMove(FEN):
    stockfish.set_fen_position(FEN)
    #print(stockfish.get_board_visual())
    #print(stockfish.get_evaluation())

    return stockfish.get_best_move()

def DisplayPieceMap(PieceType, BoardImg):
    for Color in Colors:
        DisplayMap(Color, PieceType, BoardImg)

def DisplayMap(Color, PieceType, BoardImg):
    Coords = MapPiece(Color, PieceType, BoardImg)
    print("Color:", Color, "PieceType:", PieceType, "Coords:", Coords)

def GetSquareCoords(x, y):
    ax = A1[0]
    ay = A1[1]

    bx = ax + (x * SquareSize)
    by = ay - (y * SquareSize)

    return bx, by

def MapCoords(StrCoords):
    StrCoords = StrCoords.upper()

    x = string.ascii_uppercase.index(StrCoords[0])
    y = int(StrCoords[1]) - 1

    if not IsWhite:
        y = 7 - y
        x = 7 - x

    return x, y

def GetSquare(StrCoords):
    return GetSquareCoords(*MapCoords(StrCoords))

def GoToSquare(StrCoords):
    pyautogui.moveTo(*GetSquare(StrCoords))

def Move(StrMove):
    Origin = StrMove[0:2]
    Destination = StrMove[2::]

    time.sleep(GetDelay(Destination))

    GoToSquare(Origin)
    pyautogui.dragTo(*GetSquare(Destination), MoveDelay, button='left')

    if len(Destination) > 2:
        time.sleep(0.75)
        pyautogui.click()

def ConvertColorToDouble(Color):
    r, g, b = Color

    return sRGBColor(r/255, g/255, b/255)

def GetColorDifference(C1, C2):
    # Convert from RGB to Lab Color Space
    color1_lab = convert_color(ConvertColorToDouble(C1), LabColor)

    # Convert from RGB to Lab Color Space
    color2_lab = convert_color(ConvertColorToDouble(C2), LabColor)

    # Find the color difference
    delta_e = delta_e_cie2000(color1_lab, color2_lab)

    return delta_e

def SanitizeImage(ImageName):
    im = Image.open(ImageName)
    pixels = im.load()

    width, height = im.size
    for x in range(width):
        for y in range(height):
            currentColor = pixels[x, y]
            if currentColor in ReplaceColors or IsRed(currentColor):
                pixels[x, y] = LightSquareRGB
            #diff = GetColorDifference(currentColor, DarkSquareRGB)
            #if diff < ColorThreadhold:
            #   pixels[x, y] = LightSquareRGB

    im.save(ImageName)

def CaptureSquare(StrCoords, FileName):
    x, y = GetSquareCoords(*MapCoords(StrCoords))
    Left = x - (SquareSize / 2)
    Top = y - (SquareSize / 2) - 1
    Width = SquareSize
    Height = SquareSize
    Region = (Left, Top, Width, Height)

    pyautogui.screenshot(FileName, region=Region)
    SanitizeImage(FileName)
    ConvertToGrey(FileName)

def GetPieceImages():
    PieceCoords = {
        "White" : {
            "King": "e1",
            "Queen": "d1",
            "Rook": "a1",
            "Bishop": "c1",
            "Knight": "b1",
            "Pawn": "a2"
        },
      "Black" : {
            "King": "e8",
            "Queen": "d8",
            "Rook": "a8",
            "Bishop": "c8",
            "Knight": "b8",
            "Pawn": "a7"
        }
    }

    Images = {}
    for Color in Colors:
        ColorImages = {}
        for PieceType in PieceTypes:
            FileName = PieceImageDir + Color + PieceType + ".png"
            ColorImages[PieceType] = CaptureSquare(PieceCoords[Color][PieceType], FileName)
        Images[Color] = ColorImages

def CaptureBoard():
    TopLeftCoord = "a8"

    if not IsWhite:
        TopLeftCoord = "h1"

    x, y = GetSquareCoords(*MapCoords(TopLeftCoord))
    Left = x - (SquareSize / 2)
    Top = y - (SquareSize / 2) - 1
    Width = SquareSize * 8
    Height = SquareSize * 8
    Region = (Left, Top, Width, Height)
    FileName = "BoardCapture.png"
    pyautogui.screenshot(FileName, region=Region)
    SanitizeImage(FileName)

    return FileName

def MapPiece(Color, PieceType, BoardImg):
    global Icons
    IconFileName = PieceImageDir + Color + PieceType + ".png"
    templateG = Icons[IconFileName]
    w, h = templateG.shape[::-1]

    res = cv2.matchTemplate(BoardImg, templateG, cv2.TM_CCOEFF_NORMED)

    Coords = []

    loc = np.where(res >= ConfidenceLevel)
    for pt in zip(*loc[::-1]):
        #cv2.rectangle(BoardImg, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), -1)
        xp, yp = (pt[0] + (SquareSize), pt[1] - (SquareSize))

        x = round((xp / SquareSize))
        y = 8 - round(yp / SquareSize)

        xc = string.ascii_uppercase[x - 1]
        yc = str(y - 1)

        Coords.append(xc + yc)


    #cv2.imwrite('res.png', BoardImg)

    Coords = list(set(Coords))

    if not IsWhite:
        NewCoords = []
        for Coord in Coords:
            NewCoords.append(InvertCoordinate(Coord))

        Coords = NewCoords

    Coords.sort()
    return Coords

def ConvertToGrey(Filename):
    img = cv2.imread(Filename)
    imgGrey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(Filename, imgGrey)

def MapPieces():
    imgBoardRgb = cv2.imread(CaptureBoard())
    imgBoardGrey = cv2.cvtColor(imgBoardRgb, cv2.COLOR_BGR2GRAY)


    Pieces = {}
    for Color in Colors:
        ColorPieces = {}
        for PieceType in PieceTypes:
            ColorPieces[PieceType] = MapPiece(Color, PieceType, imgBoardGrey)
        Pieces[Color] = ColorPieces

    if len(Pieces["Black"]["King"]) == 0 or len(Pieces["White"]["King"]) == 0:
        print(Pieces)
        return MapPieces()

    global CurrentPieces
    global CurrentFlippedPieces

    CurrentPieces = Pieces
    CurrentFlippedPieces = FlipPieceArray(Pieces)

    return Pieces

def DebugCycle():
    for Rank in Ranks:
        for File in Files:
            Coord = File + Rank
            print(Coord)
            GoToSquare(Coord)

def InvertCoordinate(Coord):
    Coord = Coord.upper()

    x = string.ascii_uppercase.index(Coord[0])
    y = int(Coord[1]) - 1

    x = 7 - x
    y = 8 - y

    return string.ascii_uppercase[x] + str(y)

def DebugMoves():
    Move('e2-e4')
    Move('d7-d5')
    Move('e4-d5')
    Move('d8-d5')
    Move('b1-c3')

def FlipPieceArray(PieceArray):
    FlippedPieces = {}
    for Color in Colors:
        for PieceType in PieceTypes:
            Coords = PieceArray[Color][PieceType]
            for Coord in Coords:
                FlippedPieces[Coord] = (Color, PieceType)
    return FlippedPieces

def GetFENSymbol(Piece):
    Color, PieceType = Piece

    Symbol = PieceType[0]
    if PieceType == "Knight":
        Symbol = "N"

    if Color == "Black":
        Symbol = Symbol.lower()

    return Symbol

def DoCastleLogic(FlippedPieceArray, Color):
    global Castles
    Rooks = {}
    Kings = {}

    Rooks["Black"] = ("H8", "A8") # King side, Queen Side
    Rooks["White"] = ("H1", "A1")  # King side, Queen Side
    Kings["Black"] = "E8"
    Kings["White"] = "E1"

    # If the king moves then all castles are gone
    if Castles[Color][0] or Castles[Color][1]:
        if not Kings[Color] in FlippedPieceArray:
            Castles[Color] = (False, False)

    KingRook, QueenRook = Rooks[Color]

    OutputStr = ""
    if Castles[Color][0]: # King side
        if not KingRook in FlippedPieceArray:
            Castles[Color] = (False, Castles[Color][1])
        else:
            OutputStr += "K"

    if Castles[Color][1]:  # Queen side
        if not QueenRook in FlippedPieceArray:
            Castles[Color] = (Castles[Color][0], False)
        else:
            OutputStr += "Q"

    if Color == "Black":
        return OutputStr.lower()

    if len(OutputStr) > 0:
        OutputStr += " "

    return OutputStr

def GetFEN(PieceArray):
    FileFen = []
    FlippedArray = FlipPieceArray(PieceArray)
    for Rank in Ranks:
        Blanks = 0
        Fen = ""
        for File in Files:
            Coords = File + Rank
            if Coords in FlippedArray:
                if Blanks > 0:
                    Fen += str(Blanks)
                Fen += GetFENSymbol(FlippedArray[Coords])
                Blanks = 0
            else:
                Blanks += 1
        if Blanks > 0:
            Fen += str(Blanks)
        FileFen.append(Fen)

    FinalFen = ""
    FileFen.reverse()
    for Fen in FileFen:
        Fen[::-1]
        FinalFen += Fen + '/'

    ColorSym = "w"
    if not IsWhite:
        ColorSym = "b"

    CastleStr = DoCastleLogic(FlippedArray, "White")
    CastleStr += DoCastleLogic(FlippedArray, "Black")


    return FinalFen[:-1] + " " + ColorSym + " " + CastleStr + "- 0 1"

def DebugPosition():
    while True:
        print(pyautogui.position())
        time.sleep(2)

main()