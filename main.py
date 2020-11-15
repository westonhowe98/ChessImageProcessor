import cv2
from PixelSignature import *
import keyboard
from ChessBotSettings import *
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

stockfish = stockfish.Stockfish("stockfish_20090216_x64_bmi2.exe", parameters={"Threads": 4, "Minimum Thinking Time": 5, "Hash" : 16})
stockfish.set_skill_level(9)
stockfish.set_depth(10)

CurrentFEN = ""
IsWhite = True
DoMove = False

CurrentFlippedPieces = {}

Icons = {}
Castles = {}

def main():
    #GetPieceTemplates()
    #LoadTemplates()

    #GenerateSignatures()
    Startup()
    Play()

def Startup():
    LoadSignatures()

    Reset()

    Overhead()
    GetBase()

def GetPieceTemplates():
    global CurrentFlippedPieces
    Reset()
    GetBase()

    BoardImg = CaptureBoard()

    for Piece, Coord in PieceCoordinates.items():
        TL, BR = GetRelativeSquareCorners(Coord)
        TLX, TLY = TL
        BRX, BRY = BR

        SquareImg = BoardImg[TLY:BRY, TLX:BRX]
        Filename = PieceImageDir + Piece + ".png"
        cv2.imwrite(Filename, SquareImg)

def Reset():
    global Castles
    Both = (True, True) # King side, queenside
    Castles["White"] = Both
    Castles["Black"] = Both

def GetDelay(Destination):
    return 0.001

    if Destination.upper() in CurrentFlippedPieces:
        return 0.001

    return random.betavariate(2, 5) * 8

def IsRed(Color):
    r, g, b = Color

    if r > g:
        return True

    if r > b:
        return True

    return False

def GetBase():
    global A1
    global IsWhite

    Reset()

    while True:
        A1White = pyautogui.locateCenterOnScreen(ImageResourceDir + "A1AsWhiteSimplified.png")
        H8Black = pyautogui.locateCenterOnScreen(ImageResourceDir + "H8AsBlackSimplified.png")

        Offset = (SquareSize - (RootImageSize // 2)) // 2

        if A1White != None:
            A1 = A1White
            IsWhite = True

            x, y = A1
            x += Offset
            y -= Offset

            A1 = (x, y)
            break

        if H8Black != None:
            A1 = H8Black
            IsWhite = False

            x, y = A1
            x += Offset
            y -= Offset

            A1 = (x, y)
            break



    print("Is White:", IsWhite)
    print(A1)

def IsMyTurn():
    Timer = pyautogui.locateCenterOnScreen(ImageResourceDir + "TimerSource.png")
    if Timer != None:
        x, y = Timer
        if y > (1080/2):
            return True

    Timer2 = pyautogui.locateCenterOnScreen(ImageResourceDir + "TimerSource2.png")
    if Timer2 != None:
        x, y = Timer2
        if y > (1080/2):
            GetBase()
            return True

    return False

def WaitForTurn():
    FEN = GetFEN(MapBoardSquares())

    while FEN == FEN_START and not IsWhite:
        FEN = GetFEN(MapBoardSquares())

    while True:
        if keyboard.is_pressed('q'):
            quit()

        if IsMyTurn():
            break

        Pieces = MapBoardSquares()
        NewFEN = GetFEN(Pieces)
        if(NewFEN != FEN):
            break

        Overhead()

def Overhead():

    if pyautogui.locateCenterOnScreen(ImageResourceDir + "ClaimVictory.png") != None:
        pyautogui.moveTo(pyautogui.locateCenterOnScreen(ImageResourceDir + "ClaimVictory.png"))
        pyautogui.click()
        time.sleep(0.1)
        pyautogui.moveTo(10, 10)

    if pyautogui.locateCenterOnScreen(ImageResourceDir + "NewOpponent.png") != None:
        time.sleep(2)
        pyautogui.moveTo(pyautogui.locateCenterOnScreen(ImageResourceDir + "NewOpponent.png"))
        pyautogui.click()

        time.sleep(2)


        while True:
            if pyautogui.locateCenterOnScreen(ImageResourceDir + "A1AsWhiteSimplified.png") != None:
                break

            if pyautogui.locateCenterOnScreen(ImageResourceDir + "H8AsBlackSimplified.png") != None:
                break

            GetBase()

def Play():
    print("Starting Play")

    WaitForTurn()

    while True:
        print()
        start = time.time()
        Pieces = MapBoardSquares()
        end = time.time()
        PieceMappingTime = end - start
        print("PieceMappingTime: ", PieceMappingTime, Pieces)

        start = time.time()
        FEN = GetFEN(Pieces)
        end = time.time()
        FENGenerationTime = end - start
        print("FENGenerationTime: ", FENGenerationTime, FEN)

        start = time.time()
        BestMove = GetBestMove(FEN)
        end = time.time()
        BestMoveTime =  end - start
        print("BestMoveTime: ", BestMoveTime, BestMove)

        TotalTime = PieceMappingTime + FENGenerationTime + BestMoveTime

        print("TotalTime", TotalTime)
        print()

        Move(BestMove)
        WaitForTurn()

def GetBestMove(FEN):
    stockfish.set_fen_position(FEN)
    #print(stockfish.get_board_visual())
    #print(stockfish.get_evaluation())

    return stockfish.get_best_move()

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
    if not DoMoves:
        return

    Origin = StrMove[0:2]
    Destination = StrMove[2::]

    time.sleep(GetDelay(Destination))

    GoToSquare(Origin)
    pyautogui.click()
    GoToSquare(Destination)
    pyautogui.click()
    #pyautogui.dragTo(*GetSquare(Destination), MoveDelay, button='left')

    if len(Destination) > 2:
        time.sleep(0.75)
        pyautogui.click()

    time.sleep(0.2)

def ConvertColorOrder(Color):
    r, g, b = Color
    return b, g, r

def SanitizeImage(Img):
    LightSquareBGR = ConvertColorOrder(LightSquareRGB)
    DarkSquareBGR = ConvertColorOrder(DarkSquareRGB)

    Img[np.where((Img == DarkSquareBGR).all(axis = 2))] = LightSquareBGR

def GetCoordList():
    Coords = []
    for Rank in Ranks:
        for File in Files:
            Coords.append(File + Rank)
    return Coords

def CaptureBoard():
    TopLeftCoord = "a8"

    if not IsWhite:
        TopLeftCoord = "h1"

    x, y = GetSquareCoords(*MapCoords(TopLeftCoord))
    Left = x - (SquareSize / 2)
    Top = y - (SquareSize / 2)
    Width = SquareSize * 8
    Height = SquareSize * 8
    Region = (Left, Top, Width, Height)
    FileName = "BoardCapture.png"

    pyautogui.screenshot(FileName, region=Region)

    BoardImg = cv2.imread(FileName)

    #SanitizeImage(BoardImg)

    #BoardImg = cv2.cvtColor(BoardImg, cv2.COLOR_BGR2GRAY)
    #SimplifyImage(BoardImg)
    #cv2.imwrite(FileName, BoardImg)

    return BoardImg

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

    Coords = list(set(Coords))

    if not IsWhite:
        NewCoords = []
        for Coord in Coords:
            NewCoords.append(InvertCoordinate(Coord))

        Coords = NewCoords

    Coords.sort()
    return Coords

def CheckSignatureMatch(SquareImg, Filename):
    Template = Templates[Filename]
    x, y = PixelSignatures[Filename]
    Signature = Template[y, x]

    SquareImgSignature = SquareImg[y, x]

    # print(Filename, (x, y), Signature, SquareImgSignature, Coord)

    return (Signature == SquareImgSignature).all()

def MapBoardSquare(SquareImg, Coord):
    for Color in Colors:
        for PieceType in PieceTypes:
            Filename = PieceImageDir + Color + PieceType + ".png"
            if Filename in Templates and Filename in PixelSignatures:
                # If the signature matches return the piece type
                if CheckSignatureMatch(SquareImg, Filename):
                    #cv2.imshow(Coord, SquareImg)
                    #cv2.waitKey(0)
                    #cv2.destroyAllWindows()
                    return (Color, PieceType)

    return None

def MapBoardSquares():
    global CurrentFlippedPieces

    BoardImg = CaptureBoard()
    Coords = GetCoordList()
    Pieces = {}

    for Coord in Coords:
        TL, BR = GetRelativeSquareCorners(Coord)
        TLX, TLY = TL
        BRX, BRY = BR

        SquareImg = BoardImg[TLY:BRY, TLX:BRX]

        BoardOccupant = MapBoardSquare(SquareImg, Coord)

        if BoardOccupant != None:
            Pieces[Coord] = BoardOccupant

        CurrentFlippedPieces = Pieces

    return Pieces

def GetRelativeSquareCorners(Coord):
    x, y = MapCoords(Coord)

    FullImageSize = 8 * SquareSize

    X1 = x * SquareSize
    Y1 = SquareSize * (7 - y)

    TopLeft = (X1, Y1)
    BottomRight = (X1 + SquareSize, Y1 + SquareSize)

    return (TopLeft, BottomRight)

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

    global CurrentFlippedPieces

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
        if len(OutputStr) > 0:
            OutputStr += " "

        return OutputStr.lower()

    return OutputStr

def GetFEN(PieceArray):
    FileFen = []
    #FlippedArray = FlipPieceArray(PieceArray)
    FlippedArray = PieceArray

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