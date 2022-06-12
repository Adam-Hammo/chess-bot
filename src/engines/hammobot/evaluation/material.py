import numpy as np
import os
import chess

# pawn,knight,bishop,rook,queen
MAX_CACHED_PIECES = [8,3,3,3,3] # max number of pieces to cache
WEIGHTS = {
    chess.PAWN:100,
    chess.KNIGHT:325,
    chess.BISHOP:350,
    chess.ROOK:500,
    chess.QUEEN:900
} # weighting of each piece
TABLE_PATH = f"engines/hammobot/database/material/{'-'.join(str(e) for e in MAX_CACHED_PIECES)}_{'-'.join(str(e) for e in WEIGHTS)}.npy"

class MaterialDifferenceEvaluation:
    
    def __init__(self) :
        if not os.path.exists(TABLE_PATH):
            print("First run - generating material table")
            self.table = np.ndarray((MAX_CACHED_PIECES[0]+1,MAX_CACHED_PIECES[0]+1,
                                     MAX_CACHED_PIECES[1]+1,MAX_CACHED_PIECES[1]+1,
                                     MAX_CACHED_PIECES[2]+1,MAX_CACHED_PIECES[2]+1,
                                     MAX_CACHED_PIECES[3]+1,MAX_CACHED_PIECES[3]+1,
                                     MAX_CACHED_PIECES[4]+1,MAX_CACHED_PIECES[4]+1,))
            for p1 in range(0,MAX_CACHED_PIECES[0]+1) :
                print(f"{p1}/{MAX_CACHED_PIECES[0]+1}")
                for p2 in range(0,MAX_CACHED_PIECES[0]+1) :
                    for k1 in range (0,MAX_CACHED_PIECES[1]+1) :
                        for k2 in range (0,MAX_CACHED_PIECES[1]+1) :
                            for b1 in range (0,MAX_CACHED_PIECES[2]+1) :
                                for b2 in range (0,MAX_CACHED_PIECES[2]+1) :
                                    for r1 in range (0,MAX_CACHED_PIECES[3]+1) :
                                        for r2 in range (0,MAX_CACHED_PIECES[3]+1) :
                                            for q1 in range (0,MAX_CACHED_PIECES[4]+1) :
                                                for q2 in range (0,MAX_CACHED_PIECES[4]+1) :
                                                    self.table[p1,p2,k1,k2,b1,b2,r1,r2,q1,q2] = (p1-p2)*WEIGHTS[chess.PAWN] + (k1-k2)*WEIGHTS[chess.KNIGHT] + (b1-b2)*WEIGHTS[chess.BISHOP] + (r1-r2)*WEIGHTS[chess.ROOK] + (q1-q2)*WEIGHTS[chess.QUEEN]
            np.save(TABLE_PATH, self.table)
        else :
            self.table = np.load(TABLE_PATH)

    def evaluate_material_difference(self,board):
        try :
            return self.table[
                len(board.pieces(chess.PAWN,chess.WHITE)),
                len(board.pieces(chess.PAWN,chess.BLACK)),
                len(board.pieces(chess.KNIGHT,chess.WHITE)),
                len(board.pieces(chess.KNIGHT,chess.BLACK)),
                len(board.pieces(chess.BISHOP,chess.WHITE)),
                len(board.pieces(chess.BISHOP,chess.BLACK)),
                len(board.pieces(chess.ROOK,chess.WHITE)),
                len(board.pieces(chess.ROOK,chess.BLACK)),
                len(board.pieces(chess.QUEEN,chess.WHITE)),
                len(board.pieces(chess.QUEEN,chess.BLACK)),
            ]
        except IndexError :
            # If we reach here this combination is not cached so we calc on the fly
            return ((len(board.pieces(chess.PAWN,chess.WHITE))-len(board.pieces(chess.PAWN,chess.BLACK)))*WEIGHTS[chess.PAWN]
             + (len(board.pieces(chess.KNIGHT,chess.WHITE))-len(board.pieces(chess.KNIGHT,chess.BLACK)))*WEIGHTS[chess.KNIGHT]
             + (len(board.pieces(chess.BISHOP,chess.WHITE))-len(board.pieces(chess.BISHOP,chess.BLACK)))*WEIGHTS[chess.BISHOP]
             + (len(board.pieces(chess.ROOK,chess.WHITE))-len(board.pieces(chess.ROOK,chess.BLACK)))*WEIGHTS[chess.ROOK]
             + (len(board.pieces(chess.QUEEN,chess.WHITE))-len(board.pieces(chess.QUEEN,chess.BLACK)))*WEIGHTS[chess.QUEEN])
        

if __name__ == '__main__' :
    eval = MaterialDifferenceEvaluation()
