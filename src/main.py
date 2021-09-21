import chess
import chess.svg
from engine.engine import ChessEngine
import time

if __name__ == '__main__' :
    board = chess.Board('3r2k1/p6p/1qp3p1/8/QP2nnP1/1P3N2/4P2P/R3KBR1 w Q - 0 26')

    engine = ChessEngine(side=chess.WHITE)

    while not board.is_game_over():
        t = time.time()
        engine_move = engine.calculate_next_move(board)
        print(f"Bot plays: {str(engine_move)} ({round(time.time()-t,0)}s)")
        board.push(engine_move)
        print(board.unicode())
        m = input("Move: ")
        board.push(chess.Move.from_uci(m))
        print(board.unicode())