import chess
import chess.svg
from engines.hammobot.engine import ChessEngine
import time

class Limit:
    def __init__(self):
        self.white_clock = 120
        self.black_clock = 120

if __name__ == '__main__' :
    board = chess.Board('rnbqkb1r/pp2pppp/5n2/1Bpp4/8/4PN1P/PPPP1PP1/RNBQK2R b KQkq - 1 4')

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