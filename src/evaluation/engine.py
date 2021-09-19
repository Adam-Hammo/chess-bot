from evaluation.material import MaterialDifferenceEvaluation

material_evaluator = MaterialDifferenceEvaluation()

def evaluate_board(board):
    material_evaluator.evaluate_material_difference(board)