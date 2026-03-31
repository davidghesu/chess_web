
class Piece:

    def __init__(self, color):
        self.color = color  # "white" or "black"
        self.type = None    # will be defined in derivative classes

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "pawn"

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "rook"

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "knight"

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "bishop"

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "queen"

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "king"
