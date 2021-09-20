import chess
import numpy as np

PAWN = np.array([
0,  0,  0,  0,  0,  0,  0,  0,
50, 50, 50, 50, 50, 50, 50, 50,
10, 10, 20, 30, 30, 20, 10, 10,
 5,  5, 10, 25, 25, 10,  5,  5,
 0,  0,  0, 20, 20,  0,  0,  0,
 5, -5,-10,  0,  0,-10, -5,  5,
 5, 10, 10,-20,-20, 10, 10,  5,
 0,  0,  0,  0,  0,  0,  0,  0
])

KNIGHT = np.array([
-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  0,  0,  0,-20,-40,
-30,  0, 10, 15, 15, 10,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 10, 15, 15, 10,  5,-30,
-40,-20,  0,  5,  5,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50,
])

BISHOP = np.array([
-20,-10,-10,-10,-10,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  5,  0,  0,  0,  0,  5,-10,
-20,-10,-10,-10,-10,-10,-10,-20,
])

ROOK = np.array([
  0,  0,  0,  0,  0,  0,  0,  0,
  5, 10, 10, 10, 10, 10, 10,  5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  0,  0,  0,  5,  5,  0,  0,  0
])

QUEEN = np.array([
-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5,  5,  5,  5,  0,-10,
 -5,  0,  5,  5,  5,  5,  0, -5,
  0,  0,  5,  5,  5,  5,  0, -5,
-10,  5,  5,  5,  5,  5,  0,-10,
-10,  0,  5,  0,  0,  0,  0,-10,
-20,-10,-10, -5, -5,-10,-10,-20
])

KING = np.array([
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-20,-30,-30,-40,-40,-30,-30,-20,
-10,-20,-20,-20,-20,-20,-20,-10,
 20, 20,  0,  0,  0,  0, 20, 20,
 20, 30, 10,  0,  0, 10, 30, 20
])

ps_map = {chess.PAWN: PAWN, chess.KNIGHT: KNIGHT, chess.BISHOP: BISHOP, chess.ROOK: ROOK, chess.QUEEN: QUEEN, chess.KING: KING}

def get_piece_square_value(board, piece, colour) :
    square_set = board.pieces(piece, colour)
    if len(square_set)==0 :
        return 0
    
    if colour == chess.WHITE :
        return sum(ps_map[piece][63-np.array(list(square_set))])
    else :
        return sum(ps_map[piece][np.array(list(square_set))])

def evaluate_piece_square_difference(board) :
    white_points = (
        get_piece_square_value(board, chess.PAWN, chess.WHITE) +
        get_piece_square_value(board, chess.KNIGHT, chess.WHITE) +
        get_piece_square_value(board, chess.BISHOP, chess.WHITE) +
        get_piece_square_value(board, chess.ROOK, chess.WHITE) +
        get_piece_square_value(board, chess.QUEEN, chess.WHITE) +
        get_piece_square_value(board, chess.KING, chess.WHITE)
    )
    black_points = (
        get_piece_square_value(board, chess.PAWN, chess.BLACK) +
        get_piece_square_value(board, chess.KNIGHT, chess.BLACK) +
        get_piece_square_value(board, chess.BISHOP, chess.BLACK) +
        get_piece_square_value(board, chess.ROOK, chess.BLACK) +
        get_piece_square_value(board, chess.QUEEN, chess.BLACK) +
        get_piece_square_value(board, chess.KING, chess.BLACK)
    )
    return 1-white_points/black_points if black_points != 0 else 1