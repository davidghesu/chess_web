import copy, random

PIECE_VALUES = {
    "pawn": 1, "knight": 3, "bishop": 3,
    "rook": 5, "queen": 9, "king": 0
}

def evaluate(board):
    # Score from the perspective of black (AI). Positive = good for black
    score = 0
    for row in range(8):
        for col in range(8):
            piece = board.grid[row][col]
            if piece:
                value = PIECE_VALUES[piece.type]
                score += value if piece.color == "black" else -value
    return score

def minimax(board, depth, alpha, beta, maximizing):
    # Choose the best recursive move
    color = "black" if maximizing else "white"

    if board.is_checkmate(color): return -100000 if maximizing else 100000
    if board.is_stalemate(color): return 0
    if depth == 0: return evaluate(board)

    moves = board.get_all_legal_moves(color)
    best  = float('-inf') if maximizing else float('inf')

    for start, end in moves:
        copy_board = copy.deepcopy(board)
        copy_board.move_piece(start, end)
        score = minimax(copy_board, depth - 1, alpha, beta, not maximizing)

        if maximizing:
            best  = max(best, score)
            alpha = max(alpha, score)
        else:
            best  = min(best, score)
            beta  = min(beta, score)

        if beta <= alpha:
            break  # alpha-beta pruning: take out unnecessary branches

    return best

def get_best_move(board, depth=2):
    # return best move for black
    moves = board.get_all_legal_moves("black")
    if not moves:
        return None

    random.shuffle(moves)
    best_score = float('-inf')
    best_move  = None

    for start, end in moves:
        copy_board = copy.deepcopy(board)
        copy_board.move_piece(start, end)
        score = minimax(copy_board, depth - 1, float('-inf'), float('inf'), False)
        if score > best_score:
            best_score = score
            best_move  = (start, end)

    return best_move