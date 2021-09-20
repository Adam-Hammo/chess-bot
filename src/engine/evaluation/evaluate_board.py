from engine.evaluation.material import MaterialDifferenceEvaluation
from engine.evaluation.mobility import evaluate_mobility_difference
from engine.evaluation.piece_square import evaluate_piece_square_difference

MOBILITY_WEIGHT = 10
PIECE_SQUARE_WEIGHT = 1

material_evaluator = MaterialDifferenceEvaluation()


def evaluate_board(board):
    material_feature = material_evaluator.evaluate_material_difference(board)

    mobility_feature = MOBILITY_WEIGHT * evaluate_mobility_difference(board)

    piece_square_feature = evaluate_piece_square_difference(board)

    # print(f"Material: {material_feature}, mobility: {mobility_feature}, piece square: {piece_square_feature}")

    return material_feature + mobility_feature + piece_square_feature