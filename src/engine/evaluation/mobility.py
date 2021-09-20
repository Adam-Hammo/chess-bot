import chess

def evaluate_mobility_difference(board) :
    mobility_active = len(list(board.legal_moves))
    board.push(chess.Move.null())
    mobility_inactive = len(list(board.legal_moves))
    board.pop()

    return (mobility_active - mobility_inactive) * (1 if board.turn == chess.WHITE else -1)