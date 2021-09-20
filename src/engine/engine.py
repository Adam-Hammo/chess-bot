from engine.evaluation.evaluate_board import evaluate_board
import chess.polyglot

class ChessEngine :

    def __init__(self) :
        self.opening_book = chess.polyglot.MemoryMappedReader('engine/database/openings/Human.bin')
        self.phase = 0 # 0=opening, 1=midgame, 2=endgame
        pass

    def evaluate_next_move(self, board) :
        move = None
        try :
            move = self.opening_book.weighted_choice(board)
            return move.move
        except IndexError :
            self.phase = 1
        
        board_evaluation = evaluate_board(board)
        print(f"Eval: {board_evaluation}")