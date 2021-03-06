from engines.hammobot.evaluation.material import MaterialDifferenceEvaluation, WEIGHTS as material_weights
from engines.hammobot.evaluation.piece_square import evaluate_piece_square_difference, ps_map
import chess.polyglot
import chess.syzygy
import chess
import time
from multiprocessing import Pool

CHECKMATE_SCORE = 100000
ENDGAME_FACTOR = 1000
FUTILITY_THRESHOLD = 200

material_evaluator = MaterialDifferenceEvaluation()

endgame_tablebase = chess.syzygy.open_tablebase('engines/hammobot/database/endgames/3-4-5')

class StatefulBoard:
    def __init__(self, board: chess.Board):
        self.board = board
        self.n_pieces = (
            len(board.pieces(chess.PAWN, chess.WHITE)) +
            len(board.pieces(chess.KNIGHT, chess.WHITE)) +
            len(board.pieces(chess.BISHOP, chess.WHITE)) +
            len(board.pieces(chess.ROOK, chess.WHITE)) +
            len(board.pieces(chess.QUEEN, chess.WHITE)) +
            len(board.pieces(chess.KING, chess.WHITE)) +
            len(board.pieces(chess.PAWN, chess.BLACK)) +
            len(board.pieces(chess.KNIGHT, chess.BLACK)) +
            len(board.pieces(chess.BISHOP, chess.BLACK)) +
            len(board.pieces(chess.ROOK, chess.BLACK)) +
            len(board.pieces(chess.QUEEN, chess.BLACK)) +
            len(board.pieces(chess.KING, chess.BLACK))
        )   
        self.material_diff = material_evaluator.evaluate_material_difference(board)
        self.piece_square_diff = evaluate_piece_square_difference(board, self.n_pieces)
        self.d_material_diffs = [0]*100
        self.d_n_pieces = [0]*100
        self.d_piece_square_diffs = [0]*100
        self.depth = 0
        self.is_endgame = False
        self.transposition_table = {}

    def evaluate(self):
        if o:=self.board.outcome():
            if o.termination == chess.Termination.CHECKMATE:
                return -CHECKMATE_SCORE + self.depth
            # else drawn
            return 0
        score = (self.material_diff + 0.75*self.piece_square_diff)*(1 if self.board.turn == chess.WHITE else -1)
        if self.is_endgame:
            pass
            # too slow for now
            # if endgame_score := endgame_tablebase.get_wdl(self.board):
            #     return endgame_score*ENDGAME_FACTOR + score
        return score

    def move(self, move):
        self.update_material_eval(move)
        self.update_piece_square_eval(move)
        self.board.push(move)
        self.depth+=1

    def update_material_eval(self, move):
        sign = 1 if self.board.turn == chess.WHITE else -1
        d_material_diff = 0
        d_n_pieces = 0
        if promoted := move.promotion:
            d_material_diff += sign*material_weights[promoted]
            d_material_diff -= sign*material_weights[self.board.piece_type_at(move.from_square)]
        if captured := self.board.piece_type_at(move.to_square):
            d_material_diff += sign*material_weights[captured]
            d_n_pieces -= 1
        self.material_diff += d_material_diff
        self.n_pieces += d_n_pieces
        self.d_material_diffs[self.depth] = d_material_diff
        self.d_n_pieces[self.depth] = d_n_pieces

    def update_piece_square_eval(self, move):
        # we define phase as distance from 10 to 32 pieces (inc pawns)
        # we also only consider moved pieces cos lazy
        d_piece_square_diff = 0
        moved_piece = self.board.piece_type_at(move.from_square)
        if promoted := move.promotion:
            if self.board.turn == chess.WHITE:
                d_piece_square_diff += ps_map[self.n_pieces][promoted][move.to_square^56]
                d_piece_square_diff -= ps_map[self.n_pieces][moved_piece][move.from_square^56]
            else:
                d_piece_square_diff -= ps_map[self.n_pieces][promoted][move.to_square]
                d_piece_square_diff += ps_map[self.n_pieces][moved_piece][move.from_square]
        else:
            ps_table = ps_map[self.n_pieces][moved_piece]
            if self.board.turn == chess.WHITE:
                d_piece_square_diff += ps_table[move.to_square^56]
                d_piece_square_diff -= ps_table[move.from_square^56]
            else:
                d_piece_square_diff -= ps_table[move.to_square]
                d_piece_square_diff += ps_table[move.from_square]

        if captured := self.board.piece_type_at(move.to_square):
            if self.board.turn == chess.WHITE:
                # Black piece captured - add the diff
                d_piece_square_diff += ps_map[self.n_pieces][captured][move.to_square]
            else:
                # White piece captured - subtract the diff
                d_piece_square_diff -= ps_map[self.n_pieces][captured][move.to_square^56]

        self.piece_square_diff += d_piece_square_diff
        self.d_piece_square_diffs[self.depth] = d_piece_square_diff

    def undo_move(self):
        self.board.pop()
        self.depth-=1
        self.material_diff -= self.d_material_diffs[self.depth]
        self.piece_square_diff -= self.d_piece_square_diffs[self.depth]
        self.n_pieces -= self.d_n_pieces[self.depth]


class ChessEngine:

    def __init__(self):
        print("Initialising engine...")
        self.opening_book = chess.polyglot.MemoryMappedReader(
            'engines/hammobot/database/openings/Baron.bin')
        self.phase = 0  # 0=opening, 1=midgame, 2=endgame
        self.side = None
        self.time_per_move = 30
        self.depth = 5
        self.time = None
        self.mode = 'TIME'
        self.transposition_table = {}
        self.nodes = 0
        self.prunes = 0

    def search(self, board, time_limit):
        if not self.side:
            self.side = board.turn

        if self.phase == 0:
            try:
                move = self.opening_book.weighted_choice(board)
                return move.move
            except IndexError:
                self.phase = 1

        if self.mode == "TIME":
            if self.side == chess.WHITE:
                self.time_per_move = time_limit.white_clock/20
            else:
                self.time_per_move = time_limit.black_clock/20

        self.time = time.time()
        self.nodes = 0

        args = []
        moves = list(board.legal_moves)
        for move in moves:
            board.push(move)
            if board.is_checkmate():
                return move
            args.append([board.fen(), self.mode, self.time_per_move, self.time])
            board.pop()

        with Pool(len(args)) as p:
            print(f"Searching {len(args)} trees in parallel for {self.time_per_move}s")
            res = p.starmap(perform_search, args)

        scores = []
        depth = 0
        for i,r in enumerate(res):
            depth = max(depth, r[0])
            self.nodes += r[1]
            scores.append(r[2])

        move = moves[scores.index(min(scores))]

        print(f"""
Searched {depth}-ply
    {self.nodes} board evaluations performed in {round(time.time()-self.time)}s ({round(self.nodes/(time.time()-self.time))} nodes/sec).)
    Playing {move}
        """)

        return move

def perform_search(fen, mode, time_per_move, time_start):
    board = chess.Board(fen)
    stateful_board = StatefulBoard(board)
    if len(board.piece_map()) <= 7:
        stateful_board.is_endgame = True
        phase = 2
    else:
        phase = 1

    # try returning move on timeout
    if mode == 'TIME' :

        depth = 1
        move = None
        seq = None
        nodes = 0
        score = None

        while True :
            # Only timeout on 2nd or more layer (helps in very tight situations)
            valid, seq, nodes = alpha_beta_negamax(-CHECKMATE_SCORE, CHECKMATE_SCORE, depth, stateful_board, [None]* depth, depth, time_per_move, time_start, phase, nodes, force_sequence=seq, timeout=(depth!=1))
            if fen == 'r1bq1rk1/4bppp/p1n1p3/1p1Q2B1/8/1BN2N2/PP3PPP/R3R1K1 b - - 0 13':
                print(valid, seq)
            if valid is None :
                return depth, nodes, score, move

            score = valid
            proposed_move = seq[0]
            move = proposed_move

            if abs(valid-CHECKMATE_SCORE)<100:
                print(f"Checkmate in {depth+1}")
                return depth+1, nodes, score
                
            if abs(valid+CHECKMATE_SCORE)<100:
                print(f"Checkmate in {depth+1}")
                return depth+1, nodes, score

            depth += 1
    
    elif mode == 'DEPTH' :
        valid, seq = alpha_beta_negamax(-CHECKMATE_SCORE, CHECKMATE_SCORE, depth, stateful_board, [None]*depth)
        proposed_move = seq[0]
        print(seq)
        print(f"Eval after {depth}-ply: {valid} (proposed {proposed_move})")
        move = proposed_move

        return move, depth, valid
    

# Perform alpha-beta negamax DFS 

def alpha_beta_negamax(alpha, beta, depth_rem, stateful_board, sequence, depth, time_per_move, time_start, phase, nodes, force_sequence = None, timeout = False) :
    nodes+=1
    new_sequence = [None]*(depth_rem-1)

    if timeout and (time.time() - time_start > time_per_move) :
        return None, None, nodes

    if depth_rem == 0 :
        return quiesce(alpha, beta, stateful_board, phase), sequence, nodes

    legal_moves = list(stateful_board.board.legal_moves)
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

        # futility pruning
        if depth == depth_rem:
            if not stateful_board.board.is_check() and stateful_board.evaluate() + FUTILITY_THRESHOLD < alpha:
                continue

        stateful_board.move(move)
        if force_move is not None and len(force_sequence) != 1 :
            score, new_sequence, nodes = alpha_beta_negamax(-beta, -alpha, depth_rem - 1, stateful_board, new_sequence, depth, time_per_move, time_start, phase, nodes, force_sequence=force_sequence[1:], timeout=timeout)
            force_move = None
        else : 
            score, new_sequence, nodes = alpha_beta_negamax(-beta, -alpha, depth_rem - 1, stateful_board, new_sequence, depth, time_per_move, time_start, phase, nodes, timeout=timeout)
        stateful_board.undo_move()
        if score is None :
            return None, None, nodes
        score *= -1
        if score >= beta:
            return beta, sequence, nodes
        if score > alpha:
            alpha = score
            sequence[0] = move
            sequence[1:] = new_sequence

    return alpha, sequence, nodes

def quiesce(alpha, beta, stateful_board, phase) :
    # Simple application of quiesce function, just looks at the last moved piece
    # Basically fixes up long trading sequences
    # Needs work
    stand_pat = stateful_board.evaluate()

    if stand_pat >= beta :
        return stand_pat
    if alpha < stand_pat :
        alpha = stand_pat
    prev_move = stateful_board.board.peek()
    for attacker in stateful_board.board.attackers(stateful_board.board.turn, prev_move.to_square) :
        try :
            attacking_move = stateful_board.board.find_move(attacker, prev_move.to_square)
        except ValueError :
            # piece is pinned
            continue
        stateful_board.move(attacking_move)
        score = -quiesce(-beta,-alpha,stateful_board,phase)
        stateful_board.undo_move()
        
        if score >= beta :
            return score

        # Delta pruning
        if phase != 2:
            if score + FUTILITY_THRESHOLD < alpha:
                return alpha

        if score > alpha :
            alpha = score

    return alpha