from engine.evaluation.material import MaterialDifferenceEvaluation
from engine.evaluation.mobility import evaluate_mobility_difference
from engine.evaluation.piece_square import evaluate_piece_square_difference
import chess.polyglot
import time

MOBILITY_WEIGHT = 10
PIECE_SQUARE_WEIGHT = 1

evaluation_table = {}

material_evaluator = MaterialDifferenceEvaluation()

avgs = []

def evaluate_board(board):
    # t1 = time.time()
    z_hash = chess.polyglot.zobrist_hash(board)
    if z_hash in evaluation_table :
        return evaluation_table[z_hash]
    # t2 = time.time()

    # print(f"{(t2-t1)*1000}ms to hash")

    material_feature = material_evaluator.evaluate_material_difference(board)

    # t3 = time.time()
    # print(f"{(t3-t2)*1000}ms to get material")

    # too computationally expensive
    # mobility_feature = MOBILITY_WEIGHT * evaluate_mobility_difference(board)

    # t4 = time.time()
    # print(f"{(t4-t3)*1000}ms to get mobility")

    piece_square_feature = evaluate_piece_square_difference(board)

    # t5 = time.time()
    # print(f"{(t5-t4)*1000}ms to get PSD")
    # print(f"Material: {material_feature}, mobility: {mobility_feature}, piece square: {piece_square_feature}")

    e = (material_feature + piece_square_feature) * (1 if board.turn == chess.WHITE else -1)

    evaluation_table[z_hash] = e

    # t6 = time.time()
    # print(f"{(t6-t5)*1000}ms to calc and store")
    # print(f"{(t6-t1)*1000}ms to total")


    return e