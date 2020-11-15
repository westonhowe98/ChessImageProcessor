# ChessImageProcessor
Plays chess on lichess.com using the stockfish algorithm. 

Board state is read from screen and fed into stockfish via pixel signature matching of the pieces.
In order for this to work piece set must be changed to the one the templates are calculated for.
Or the templates must be recaptured and processed to find a unique pixel signature for each piece.
