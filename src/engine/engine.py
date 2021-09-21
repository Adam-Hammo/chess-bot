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
        self.time_per_move = 30
        self.depth = 4
        self.time = None
        self.mode = 'TIME'
        self.transposition_table = {}
        self.evals = 0
        pass

    def calculate_next_move(self, board):
        try:
            move = self.opening_book.weighted_choice(board)
            return move.move
        except IndexError:
            self.phase = 1

        self.time = time.time()
        self.evals = 0

        board = copy.deepcopy(board)
        move, depth = self.perform_search(board)

        print(f"{depth}-ply search")

        return move

    def perform_search(self, board):
        # try returning move on timeout
        if self.mode == 'TIME' :

            depth = 1
            move = None
            seq = None

            print(f"Eval after 0-ply: {evaluate_board(board)}")
            while True :
                if self.side == chess.WHITE:
                    valid, seq = self.alpha_beta_negamax(-math.inf, math.inf, chess.Move.null(), depth, board, [None]*depth, force_sequence=seq, timeout=True)
                else :
                    valid, seq = self.alpha_beta_negamax(math.inf, -math.inf, chess.Move.null(), depth, board, [None]*depth, force_sequence=seq, timeout=True)
                if valid is None :
                    print(f"{self.evals} board evaluations performed ({round(self.evals/self.time_per_move)}nodes/sec).")
                    return move, depth-1

                if valid == math.inf:
                    return proposed_move, depth

                proposed_move = seq[0]
                print(seq)
                print(f"Eval after {depth}-ply: {valid} (proposed {proposed_move})")
                move = proposed_move
                depth += 1
        
        elif self.mode == 'DEPTH' :
            if self.side == chess.WHITE:
                valid, seq = self.alpha_beta_negamax(-math.inf, math.inf, chess.Move.null(), self.depth, board, [None]*self.depth)
            else :
                valid, seq = self.alpha_beta_negamax(math.inf, -math.inf, chess.Move.null(), self.depth, board, [None]*self.depth)
            proposed_move = seq[0]
            print(seq)
            print(f"Eval after {self.depth}-ply: {valid} (proposed {proposed_move})")
            move = proposed_move

            return move, self.depth
        

    # Perform alpha-beta negamax DFS 

    def cache(self, score, sequence) :
        # self.transposition_table[hash] = score, sequence
        return score, sequence

    def alpha_beta_negamax(self, alpha, beta, prev_move, depth_rem, board, sequence, force_sequence = None, timeout = False) :

        new_sequence = [None]*(depth_rem-1)

        if (time.time() - self.time > self.time_per_move) and timeout:
            return None, None

        if depth_rem == 0:
            return self.cache(self.quiesce(alpha, beta, board), sequence)

        if board.is_checkmate() :
            if self.side == board.turn :
                return self.cache(math.inf, sequence)
            else :
                return self.cache(-math.inf, sequence)
        if board.is_stalemate() :
            return self.cache(0, sequence)

        legal_moves = list(board.legal_moves)
        if force_sequence is not None :
            # check the previous best path first
            try :
                force_move = force_sequence[0]
                legal_moves.remove(force_move)
                legal_moves.insert(0,force_move)
            except ValueError :
                force_move = None
        else :
            force_move = None

        for move in legal_moves:

            board.push(move)
            if force_move is not None and len(force_sequence) != 1 :
                score, new_sequence = self.alpha_beta_negamax(-beta, -alpha, move, depth_rem - 1, board, new_sequence, force_sequence=force_sequence[1:], timeout=timeout)
                force_move = None
            else : 
                score, new_sequence = self.alpha_beta_negamax(-beta, -alpha, move, depth_rem - 1, board, new_sequence, timeout=timeout)

            board.pop()
            if score is None :
                return None, None
            score = -score
            if score >= beta:
                return self.cache(beta, sequence)
            if score > alpha:
                alpha = score
                sequence[0] = move
                sequence[1:] = new_sequence

        return self.cache(alpha, sequence)

    def quiesce(self, alpha, beta, board) :
        # Simple application of quiesce function, just looks at the last moved piece
        # Basically fixes up long trading sequences
        # Needs work
        self.evals += 1
        stand_pat = evaluate_board(board)

        if stand_pat >= beta :
            return stand_pat
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
                return score
            if score > alpha :
                alpha = score

        return alpha