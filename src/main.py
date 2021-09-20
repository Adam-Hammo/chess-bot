import chess
import chess.svg
from engine.engine import ChessEngine
import time

if __name__ == '__main__' :
    board = chess.Board('r1b1kb1r/pp2ppp1/2n2n2/7p/Q1Pq4/8/PP3PPP/RNB1KBNR w KQkq - 0 7')

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