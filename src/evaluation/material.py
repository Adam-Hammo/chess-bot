import numpy as np
import os

# pawn,knight,bishop,rook,queen
MAX_CACHED_PIECES = [8,3,3,3,3] # max number of pieces to cache
WEIGHTS = [100,325,350,500,900] # weighting of each piece
TABLE_PATH = f"database/material/{'-'.join(str(e) for e in MAX_CACHED_PIECES)}_{'-'.join(str(e) for e in WEIGHTS)}.npy"

class MaterialDifferenceEvaluation:
    
    def __init__(self) :
        if not os.path.exists(TABLE_PATH):
            print("First run - generating material table")
            self.table = np.ndarray((9,9,3,3,3,3,3,3,3,3))
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
                                                    self.table[[p1,p2,k1,k2,b1,b2,r1,r2,q1,q2]] = (p1-p2)*WEIGHTS[0] + (k1-k2)*WEIGHTS[1] + (b1-b2)*WEIGHTS[2] + (r1-r2)*WEIGHTS[3] + (q1-q2)*WEIGHTS[4]
            np.save(TABLE_PATH, self.table)
        else :
            self.table = np.load(TABLE_PATH)

    def evaluate_material_difference(self,board):
        pass
        

if __name__ == '__main__' :
    eval = MaterialDifferenceEvaluation()
