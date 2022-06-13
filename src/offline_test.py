import chess
import chess.svg
from engines.hammobot.engine import ChessEngine
import time

class Limit:
    def __init__(self):
        self.white_clock = 300
        self.black_clock = 300

if __name__ == '__main__' :
    board = chess.Board('r2q1rk1/1Q2bppp/1p1p4/p3p3/4P3/5N2/PPP2PPP/2R2RK1 b - - 1 16')

    engine = ChessEngine()
    engine_move = engine.search(board, Limit())
    print(engine_move)
    # while not board.is_game_over():
    #     t = time.time()
    #     engine_move = engine.search(board)
    #     print(f"Bot plays: {str(engine_move)} ({round(time.time()-t,0)}s)")
    #     board.push(engine_move)
    #     print(board.unicode())
    #     m = input("Move: ")
    #     board.push(chess.Move.from_uci(m))
    #     print(board.unicode())