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
        self.time_per_move = 600
        self.time = None
        self.transposition_table = {}
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
        # try returning move on timeout
        depth = 1
        move = None
        print(f"Eval after 0-ply: {evaluate_board(board)}")
        while True :
            if self.side == chess.WHITE:
                valid, proposed_move = self.alpha_beta_negamax(-math.inf, math.inf, chess.Move.null(), depth, board)
            else :
                valid, proposed_move = self.alpha_beta_min(math.inf, -math.inf, chess.Move.null(), depth, board)
            print(f"Eval after {depth}-ply: {valid} (proposed {proposed_move})")
            if valid is None :
                return move, depth-1
            move = proposed_move
            depth += 1

    # Perform alpha-beta negamax DFS 

    def cache(self, score, move, hash) :
        self.transposition_table[hash] = score, move
        return score, move

    def alpha_beta_negamax(self, alpha, beta, prev_move, depth_rem, board) :
        if time.time() - self.time > self.time_per_move :
            return None, None

        hash_tup = (chess.polyglot.zobrist_hash(board), depth_rem)
        if (res:=self.transposition_table.get(hash_tup)) is not None :
            return res

        if depth_rem == 0:
            return self.cache(self.quiesce(alpha,beta,board), board.peek(), hash_tup)

        if board.is_checkmate() :
            return self.cache(math.inf, prev_move, hash_tup)
        if board.is_stalemate() :
            return self.cache(0, prev_move, hash_tup)

        alpha_move = None

        for move in board.legal_moves:
            board.push(move)
            score, _ = self.alpha_beta_negamax(-beta, -alpha, move, depth_rem - 1, board)
            score = -score
            board.pop()
            if score is None :
                return None, None
            if score >= beta:
                return self.cache(beta, move, hash_tup)
            if score > alpha:
                alpha = score
                alpha_move = move
        
        return self.cache(alpha, alpha_move, hash_tup)

    def quiesce(self, alpha, beta, board) :
        # Simple application of quiesce function, just looks at the last moved piece
        # Basically fixes up long trading sequences
        # Needs work

        stand_pat = evaluate_board(board)
        # return stand_pat
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