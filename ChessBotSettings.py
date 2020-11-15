FEN_START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

MoveDelay = 0.15
ConfidenceLevel = 0.80

ColorThreadhold = 10

OriginalPieceSize = 60

RootImageSize = 12 # pixel size of square image used to find board and base coordinates

DarkSquareRGB = (181, 136, 99)
LightSquareRGB = (240, 217, 181)

A1 = False
SquareSize = 92

PieceImageDir = "ProcessedPieceTemplates/"

PieceIconSignatures = {}

Files = "ABCDEFGH"
Ranks = "12345678"

SignatureFile = "TemplatePixelSignatures.csv"
ImageResourceDir = "ElementImages/"

ClockBackgroundLocation = (1344, 706)
ClockBackgroundColor = (208, 224, 189)

ReplaceColors = [
    DarkSquareRGB,
    (170,162,58),
    (205,210,106)
]

Colors = {"White", "Black"}
PieceTypes = {"King", "Queen", "Rook", "Bishop", "Knight", "Pawn"}
PieceCoordinates = {
    "BlackKing" : "E8",
    "BlackQueen" : "D8",
    "BlackRook" : "A8",
    "BlackBishop" : "C8",
    "BlackKnight" : "B8",
    "BlackPawn" : "A7",
    "WhiteKing" : "E1",
    "WhiteQueen" : "D1",
    "WhiteRook" : "A1",
    "WhiteBishop" : "C1",
    "WhiteKnight" : "B1",
    "WhitePawn" : "A2",
    "BlankSquare" : "A3"
}

DoMoves = True

UseCorrespondence = True