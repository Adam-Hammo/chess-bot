import chess
import chess.svg
from engines.hammobot.engine import ChessEngine
import time

class Limit:
    def __init__(self):
        self.white_clock = 120
        self.black_clock = 120

if __name__ == '__main__' :
    board = chess.Board('r3r1k1/6pp/p5P1/5p1Q/1pPpqN2/1P6/P6P/5RK1 b - - 0 28')

    engine = ChessEngine()
    engine_move = engine.search(board, Limit())
    # while not board.is_game_over():
    #     t = time.time()
    #     engine_move = engine.search(board)
    #     print(f"Bot plays: {str(engine_move)} ({round(time.time()-t,0)}s)")
    #     board.push(engine_move)
    #     print(board.unicode())
    #     m = input("Move: ")
    #     board.push(chess.Move.from_uci(m))
    #     print(board.unicode())