# board.py
# Handles Connect Four board state and rules

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2

def create_board():
    """Create an empty board."""
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def print_pretty_board(board):
    """Print the board in a human-readable format."""
    print("0 1 2 3 4 5 6")
    for row in board:
        print(" ".join(["X" if cell == PLAYER1 else "O" if cell == PLAYER2 else "." for cell in row]))
    print()

def is_valid_move(board, col):
    """Return True if column has space."""
    return board[0][col] == EMPTY

def get_valid_moves(board):
    """Return list of columns where moves are possible."""
    return [c for c in range(COLS) if is_valid_move(board, c)]

def make_move(board, col, piece):
    """Place piece in lowest available row. Returns True if successful."""
    for row in reversed(range(ROWS)):
        if board[row][col] == EMPTY:
            board[row][col] = piece
            return True
    return False

def undo_move(board, col):
    """Remove the top piece from a column."""
    for row in range(ROWS):
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            return True
    return False

def check_win(board, piece):
    """Check if the given piece has four in a row."""
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    # Vertical
    for c in range(COLS):
        for r in range(ROWS-3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    # Diagonal /
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    # Diagonal \
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    return False

def check_draw(board):
    """Check if the board is full (top row has no empty cells)."""
    return all(board[0][c] != EMPTY for c in range(COLS))
