from engine.evaluation.evaluate_board import evaluate_board
import chess.polyglot
import math
import chess
import time
import copy

class ChessEngine:

    def __init__(self, side):
        self.opening_book = chess.polyglot.MemoryMappedReader(
            'engine/database/openings/Baron.bin')
        self.phase = 0  # 0=opening, 1=midgame, 2=endgame
        self.side = side
        self.time_per_move = 20
        self.time = None
        pass

    def calculate_next_move(self, board):
        try:
            move = self.opening_book.weighted_choice(board)
            return move.move
        except IndexError:
            self.phase = 1

        self.time = time.time()

        board = copy.deepcopy(board)
        move, depth = self.perform_search(board)

        print(f"{depth}-ply search")

        return move

    def perform_search(self, board):
        depth = 1
        move = None
        while True :
            if self.side == chess.WHITE:
                valid, proposed_move = self.alpha_beta_max(-math.inf, math.inf, chess.Move.null(), depth, board, force_move=move)
            else :
                valid, proposed_move = self.alpha_beta_min(-math.inf, math.inf, chess.Move.null(), depth, board, force_move=move)
            if valid is None :
                return move, depth-1
            move = proposed_move
            depth += 1

    # Perform alpha-beta max-min DFS 

    def alpha_beta_max(self, alpha, beta, prev_move, depth_rem, board, force_move = None):
        if time.time() - self.time > self.time_per_move :
            return None, None
        if depth_rem == 0:
            return self.quiesce(alpha,beta,board), board.peek()
        alpha_move = None
        if board.is_checkmate() :
            return -math.inf, prev_move
        if board.is_stalemate() :
            return 0, prev_move

        legal_moves = list(board.legal_moves)
        if force_move is not None :
            legal_moves.remove(force_move)
            legal_moves.insert(0,force_move)

        for move in legal_moves:
            board.push(move)
            score, _ = self.alpha_beta_min(alpha, beta, move, depth_rem - 1, board)
            if score is None :
                return None, None
            board.pop()
            if score >= beta:
                return beta, move
            if score > alpha:
                alpha = score
                alpha_move = move
        return alpha, alpha_move

    def alpha_beta_min(self, alpha, beta, prev_move, depth_rem, board, force_move = None):
        if time.time() - self.time > self.time_per_move :
            return None, None
        if depth_rem == 0:
            return self.quiesce(alpha,beta,board), board.peek()
        beta_move = None
        if board.is_checkmate() :
            return math.inf, prev_move
        if board.is_stalemate() :
            return 0, prev_move

        legal_moves = list(board.legal_moves)
        if force_move is not None :
            legal_moves.remove(force_move)
            legal_moves.insert(0,force_move)

        for move in board.legal_moves:
            board.push(move)
            score, _ = self.alpha_beta_max(alpha, beta, move, depth_rem - 1, board)
            if score is None :
                return None, None
            board.pop()
            if score <= alpha:
                return alpha, move
            if score < beta:
                beta = score
                beta_move = beta
        return beta, beta_move

    def quiesce(self, alpha, beta, board) :
        # Simple application of quiesce function, just looks at the last moved piece
        # Basically fixes up long trading sequences
        # Needs work

        stand_pat = evaluate_board(board)
        if stand_pat >= beta :
            return beta
        if alpha < stand_pat :
            alpha = stand_pat

        prev_move = board.peek()
        for attacker in board.attackers(board.turn, prev_move.to_square) :
            try :
                attacking_move = board.find_move(attacker, prev_move.to_square)
            except ValueError :
                # piece is pinned
                continue
            board.push(attacking_move)
            score = -self.quiesce(-beta,-alpha,board)
            board.pop()
            if score >= beta :
                return beta
            if score > alpha :
                alpha = score

        return alpha