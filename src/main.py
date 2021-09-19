import chess
from evaluation import engine as EvaluationEngine

if __name__ == '__main__' :
    board = chess.Board()
    EvaluationEngine.evaluate_board(board)
    