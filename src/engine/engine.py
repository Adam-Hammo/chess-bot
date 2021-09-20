from engine.evaluation.evaluate_board import evaluate_board
import chess.polyglot
import math
import chess

class ChessEngine:

    def __init__(self, side):
        self.opening_book = chess.polyglot.MemoryMappedReader(
            'engine/database/openings/Human.bin')
        self.phase = 0  # 0=opening, 1=midgame, 2=endgame
        self.side = side
        pass

    def evaluate_next_move(self, board):
        move = None
        try:
            move = self.opening_book.weighted_choice(board)
            return move.move
        except IndexError:
            self.phase = 1

        if self.side == chess.WHITE:
            _, move = self.alpha_beta_max(-math.inf, math.inf, 4, board)
        else :
            _, move = self.alpha_beta_min(-math.inf, math.inf, 4, board)
        return move



    # Perform alpha-beta DFS

    def alpha_beta_max(self, alpha, beta, depth_rem, board):
        if depth_rem == 0:
            return evaluate_board(board), board.peek()
        alpha_move = None
        for move in board.legal_moves:
            board.push(move)
            score, _ = self.alpha_beta_min(alpha, beta, depth_rem - 1, board)
            board.pop()
            if score >= beta:
                return beta, move
            if score > alpha:
                alpha = score
                alpha_move = move
        return alpha, alpha_move

    def alpha_beta_min(self, alpha, beta, depth_rem, board):
        if depth_rem == 0:
            return evaluate_board(board)
        beta_move = None
        for move in board.legal_moves:
            board.push(move)
            score, _ = self.alpha_beta_max(alpha, beta, depth_rem - 1, board)
            board.pop()
            if score <= alpha:
                return alpha, move
            if score < beta:
                beta = score
                beta_move = beta
        return beta, beta_move
