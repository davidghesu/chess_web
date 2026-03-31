from logic.pieces import Pawn, Rook, Knight, Bishop, Queen, King
from logic.move import Move


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.turn = "white"
        self.move_history = []

        # for castling
        self.white_king_moved = False
        self.white_rook_left_moved = False
        self.white_rook_right_moved = False
        self.black_king_moved = False
        self.black_rook_left_moved = False
        self.black_rook_right_moved = False

        self.en_passant_target = None

        # for repetition draw
        self.position_history = []

    def initialize_board(self):
        for col in range(8):
            self.grid[1][col] = Pawn("white")
            self.grid[6][col] = Pawn("black")

        # rooks
        self.grid[0][0] = Rook("white")
        self.grid[0][7] = Rook("white")
        self.grid[7][0] = Rook("black")
        self.grid[7][7] = Rook("black")

        # knights
        self.grid[0][1] = Knight("white")
        self.grid[0][6] = Knight("white")
        self.grid[7][1] = Knight("black")
        self.grid[7][6] = Knight("black")

        # bishops
        self.grid[0][2] = Bishop("white")
        self.grid[0][5] = Bishop("white")
        self.grid[7][2] = Bishop("black")
        self.grid[7][5] = Bishop("black")

        # queens
        self.grid[0][3] = Queen("white")
        self.grid[7][3] = Queen("black")

        # kings
        self.grid[0][4] = King("white")
        self.grid[7][4] = King("black")

    def get_piece(self, position):
        row, col = position
        return self.grid[row][col]

    def set_piece(self, position, piece):
        row, col = position
        self.grid[row][col] = piece


    #
    def get_position_key(self):
        """ Transform the current position into a unique string. Two identical positions will produce the same string."""
        key = ""
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece:
                    key += f"{row}{col}{piece.color[0]}{piece.type[0]}"
                else:
                    key += "__"
        # Include the row and en passant so that they are truly identical positions
        key += self.turn
        key += str(self.en_passant_target)
        return key

    def is_threefold_repetition(self):
        """ Returns True if the current position has appeared 3 times."""
        current = self.get_position_key()
        return self.position_history.count(current) >= 3

    def is_insufficient_material(self):
        # Returns True if there is no check mate
        pieces = {"white": [], "black": []}

        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.type != "king":
                    pieces[piece.color].append((piece.type, row, col))

        white = pieces["white"]
        black = pieces["black"]

        # King vs King
        if not white and not black:
            return True

        # King + bishop/knight vs king
        if not black and len(white) == 1 and white[0][0] in ("bishop", "knight"):
            return True
        if not white and len(black) == 1 and black[0][0] in ("bishop", "knight"):
            return True

        # King + bishop vs king + bishop (same color bishops)
        if len(white) == 1 and len(black) == 1:
            if white[0][0] == "bishop" and black[0][0] == "bishop":
                # square color = (row + col) % 2
                white_sq = (white[0][1] + white[0][2]) % 2
                black_sq = (black[0][1] + black[0][2]) % 2
                if white_sq == black_sq:
                    return True

        return False

    def is_draw(self):
        return self.is_threefold_repetition() or self.is_insufficient_material()

    def is_valid_move(self, start, end):
        piece = self.get_piece(start)
        if piece is None or piece.color != self.turn:
            return False

        target = self.get_piece(end)
        if target and target.color == piece.color:
            return False

        sr, sc = start
        er, ec = end

        if piece.type == "pawn":
            if piece.color == "white":
                if er == sr + 1 and abs(ec - sc) == 1 and target is None:
                    if self.en_passant_target == (er, ec):
                        return True
                return Move.white_pawn_move_check(er, ec, self.grid, sr, sc, piece)
            else:
                if er == sr - 1 and abs(ec - sc) == 1 and target is None:
                    if self.en_passant_target == (er, ec):
                        return True
                return Move.black_pawn_move_check(er, ec, self.grid, sr, sc, piece)
        elif piece.type == "rook":
            return Move.rook_move_check(er, ec, self.grid, sr, sc, piece)
        elif piece.type == "knight":
            return Move.knight_move_check(er, ec, sr, sc)
        elif piece.type == "bishop":
            return Move.bishop_move_check(er, ec, self.grid, sr, sc, piece)
        elif piece.type == "queen":
            return Move.queen_move_check(er, ec, self.grid, sr, sc, piece)
        elif piece.type == "king":
            if abs(ec - sc) == 2 and er == sr:
                return self.is_castling_valid(start, end)
            return Move.king_move_check(er, ec, self.grid, sr, sc, piece)

        return False

    def is_castling_valid(self, start, end):
        sr, sc = start
        er, ec = end
        piece = self.get_piece(start)

        if piece.type != "king":
            return False

        if piece.color == "white" and self.white_king_moved:
            return False
        if piece.color == "black" and self.black_king_moved:
            return False

        if self.in_check(piece.color):
            return False

        # right castling
        if ec == sc + 2:
            if piece.color == "white":
                if self.white_rook_right_moved:
                    return False
                rook = self.grid[0][7]
            else:
                if self.black_rook_right_moved:
                    return False
                rook = self.grid[7][7]

            if not rook or rook.type != "rook":
                return False

            for col in range(sc + 1, 7):
                if self.grid[sr][col] is not None:
                    return False

            # checking every position for king
            for col in [sc, sc + 1, sc + 2]:
                temp_piece = self.grid[sr][col]
                saved_turn = self.turn
                self.grid[sr][col] = piece
                self.grid[sr][sc] = None
                in_check = self.in_check(piece.color)
                self.grid[sr][sc] = piece
                self.grid[sr][col] = temp_piece
                self.turn = saved_turn
                if in_check:
                    return False
            return True

        # left castling
        elif ec == sc - 2:
            if piece.color == "white":
                if self.white_rook_left_moved:
                    return False
                rook = self.grid[0][0]
            else:
                if self.black_rook_left_moved:
                    return False
                rook = self.grid[7][0]

            if not rook or rook.type != "rook":
                return False

            for col in range(1, sc):
                if self.grid[sr][col] is not None:
                    return False

            # checking every position for king
            for col in [sc, sc - 1, sc - 2]:
                temp_piece = self.grid[sr][col]
                saved_turn = self.turn
                self.grid[sr][col] = piece
                self.grid[sr][sc] = None
                in_check = self.in_check(piece.color)
                self.grid[sr][sc] = piece
                self.grid[sr][col] = temp_piece
                self.turn = saved_turn
                if in_check:
                    return False
            return True

        return False

    def is_legal_move(self, start, end):
        piece = self.get_piece(start)

        if piece is None:
            return False

        if not self.is_valid_move(start, end):
            return False

        color = piece.color

        if piece.type == "king" and abs(end[1] - start[1]) == 2:
            return True


        saved_start = self.grid[start[0]][start[1]]
        saved_end = self.grid[end[0]][end[1]]
        saved_en_passant = None

        # simulation for en passant. (deleting the captured pawn)
        if piece.type == "pawn" and self.en_passant_target == end:
            if piece.color == "white":
                saved_en_passant = self.grid[end[0] - 1][end[1]]
                self.grid[end[0] - 1][end[1]] = None
            else:
                saved_en_passant = self.grid[end[0] + 1][end[1]]
                self.grid[end[0] + 1][end[1]] = None

        # simulation
        self.grid[end[0]][end[1]] = saved_start
        self.grid[start[0]][start[1]] = None

        # checking if the move was legal
        in_check = self.in_check(color)

        # coming back
        self.grid[start[0]][start[1]] = saved_start
        self.grid[end[0]][end[1]] = saved_end

        if saved_en_passant:
            if piece.color == "white":
                self.grid[end[0] - 1][end[1]] = saved_en_passant
            else:
                self.grid[end[0] + 1][end[1]] = saved_en_passant

        return not in_check

    def move_piece(self, start, end, promotion_choice="queen"):
        piece = self.get_piece(start)
        captured = self.get_piece(end)

        if piece is None or not self.is_legal_move(start, end):
            return False

        sr, sc = start
        er, ec = end

        # special case for en passant.
        en_passant_capture = False
        if piece.type == "pawn" and self.en_passant_target == end and captured is None:
            en_passant_capture = True
            if piece.color == "white":
                captured = self.grid[er - 1][ec]
                self.grid[er - 1][ec] = None
            else:
                captured = self.grid[er + 1][ec]
                self.grid[er + 1][ec] = None

        # old_en_passant = self.en_passant_target
        self.en_passant_target = None

        if piece.type == "pawn" and abs(er - sr) == 2:
            if piece.color == "white":
                self.en_passant_target = (sr + 1, sc)
            else:
                self.en_passant_target = (sr - 1, sc)

        # special case for castling. two pieces move
        is_castling = False
        if piece.type == "king" and abs(ec - sc) == 2:
            is_castling = True
            if ec == sc + 2:
                rook = self.grid[sr][7]
                self.grid[sr][5] = rook
                self.grid[sr][7] = None
            else:
                rook = self.grid[sr][0]
                self.grid[sr][3] = rook
                self.grid[sr][0] = None

        self.set_piece(end, piece)
        self.set_piece(start, None)

        # sets all the parameters for castling
        if piece.type == "king":
            if piece.color == "white":
                self.white_king_moved = True
            else:
                self.black_king_moved = True
        elif piece.type == "rook":
            if piece.color == "white":
                if sc == 0:
                    self.white_rook_left_moved = True
                elif sc == 7:
                    self.white_rook_right_moved = True
            else:
                if sc == 0:
                    self.black_rook_left_moved = True
                elif sc == 7:
                    self.black_rook_right_moved = True

        # special case for promotion
        promotion = None
        promoted_piece = piece
        if piece.type == "pawn" and (er == 0 or er == 7):
            promotion = promotion_choice
            if promotion == "queen":
                promoted_piece = Queen(piece.color)
            elif promotion == "rook":
                promoted_piece = Rook(piece.color)
            elif promotion == "bishop":
                promoted_piece = Bishop(piece.color)
            elif promotion == "knight":
                promoted_piece = Knight(piece.color)
            else:
                promoted_piece = Queen(piece.color)
            self.set_piece(end, promoted_piece)

        # completing move
        move = Move(start=start, end=end, piece_moved=promoted_piece, piece_captured=captured, promotion=promotion)
        move.is_castling = is_castling
        move.is_en_passant = en_passant_capture
        self.move_history.append(move)

        self.turn = "black" if self.turn == "white" else "white"

        # it saves the position after the move to detect the repetition
        self.position_history.append(self.get_position_key())

        return True

    def in_check(self, color):
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.type == "king" and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        enemy_color = "black" if color == "white" else "white"
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == enemy_color:
                    saved_turn = self.turn
                    self.turn = enemy_color
                    can_attack = self.is_valid_move((row, col), king_pos)
                    self.turn = saved_turn
                    if can_attack:
                        return True
        return False

    def is_checkmate(self, color):
        if self.in_check(color) and not self.get_all_legal_moves(color):
            return True
        return False

    def is_stalemate(self, color):
        if not self.in_check(color) and not self.get_all_legal_moves(color):
            return True
        return False

    def get_all_legal_moves(self, color):
        legal_moves = []
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    for r in range(8):
                        for c in range(8):
                            start = (row, col)
                            end = (r, c)
                            if self.is_legal_move(start, end):
                                legal_moves.append((start, end))
        return legal_moves