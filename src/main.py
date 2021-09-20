import chess
import chess.svg
from engine.engine import ChessEngine

if __name__ == '__main__' :
    board = chess.Board()

    engine = ChessEngine(side=chess.WHITE)

    while not board.is_game_over():
        engine_move = engine.evaluate_next_move(board)
        print("Bot plays: " + str(engine_move))
        board.push(engine_move)
        print(board.unicode())
        m = input("Move: ")
        board.push(chess.Move.from_uci(m))
        print(board.unicode())