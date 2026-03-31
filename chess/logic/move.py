class Move:

    def __init__(self, start, end, piece_moved, piece_captured=None, promotion=None):

        self.start = start
        self.end = end
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured
        self.promotion = promotion
        self.is_castling = False
        self.is_en_passant = False

    def __repr__(self):
        return f"{self.piece_moved} from {self.start} to {self.end}" + (f", captures {self.piece_captured}" if self.piece_captured else "")

    @staticmethod
    def white_pawn_move_check(row, col, board, selected_row, selected_col, selected_piece):
        # basic move
        if col == selected_col and row == selected_row + 1 and board[row][col] is None:
            return True
        # double move
        if selected_row == 1 and row == selected_row + 2 and col == selected_col and board[row][col] is None and board[selected_row + 1][selected_col] is None:
            return True
        # capture
        if row == selected_row + 1 and abs(col - selected_col) == 1 and board[row][col] is not None and board[row][col].color != selected_piece.color:
            return True
        return False


    @staticmethod
    def black_pawn_move_check(row, col, board, selected_row, selected_col, selected_piece):

        if col == selected_col and row == selected_row - 1 and board[row][col] is None:
            return True

        if selected_row == 6 and row == selected_row - 2 and col == selected_col and board[row][col] is None and board[selected_row - 1][selected_col] is None:
            return True

        if row == selected_row - 1 and abs(col - selected_col) == 1 and board[row][col] is not None and board[row][col].color != selected_piece.color:
            return True
        return False


    @staticmethod
    def rook_move_check(row, col, board, selected_row, selected_col, selected_piece):

        if col == selected_col:
            step = 1 if row > selected_row else -1
            for r in range(selected_row + step, row, step):
                if board[r][col] is not None:
                    return False
        elif row == selected_row:
            step = 1 if col > selected_col else -1
            for c in range(selected_col + step, col, step):
                if board[row][c] is not None:
                    return False
        else:
            return False

        target = board[row][col]
        if target and target.color == selected_piece.color:
            return False

        return True


    @staticmethod
    def knight_move_check(row, col, selected_row, selected_col):
        dx = abs(row - selected_row)
        dy = abs(col - selected_col)
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)


    @staticmethod
    def king_move_check(row, col, board, selected_row, selected_col, selected_piece):
        dx = abs(row - selected_row)
        dy = abs(col - selected_col)
        if dx > 1 or dy > 1:
            return False
        target = board[row][col]
        if target and target.color == selected_piece.color:
            return False
        return True


    @staticmethod
    def bishop_move_check(row, col, board, selected_row, selected_col, selected_piece):
        dx = abs(row - selected_row)
        dy = abs(col - selected_col)
        if dx != dy:
            return False

        row_step = 1 if row > selected_row else -1
        col_step = 1 if col > selected_col else -1
        r, c = selected_row + row_step, selected_col + col_step
        while r != row and c != col:
            if board[r][c] is not None:
                return False
            r += row_step
            c += col_step

        target = board[row][col]
        if target and target.color == selected_piece.color:
            return False

        return True


    @staticmethod
    def queen_move_check(row, col, board, selected_row, selected_col, selected_piece):
        return Move.rook_move_check(row, col, board, selected_row, selected_col, selected_piece) or \
            Move.bishop_move_check(row, col, board, selected_row, selected_col, selected_piece)
