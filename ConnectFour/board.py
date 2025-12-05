# board.py
# This file handles the Connect Four board representation and game rules.

ROWS = 6   # number of rows
COLS = 7   # number of columns

def create_board():
    """Create an empty 6x7 board represented as a list of lists."""
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def print_board(board):
    """Print the board in a human-friendly way."""
    for row in board:
        print(row)
    print("\n")

def is_valid_move(board, col):
    """Check if a column has space for a move."""
    return board[0][col] == 0

def get_valid_moves(board):
    """Return a list of columns where a move is possible."""
    return [c for c in range(COLS) if is_valid_move(board, c)]

def make_move(board, col, piece):
    """
    Place a piece (1=human, 2=AI) in the lowest available row of the chosen column.
    Returns True if move successful, False otherwise.
    """
    for row in reversed(range(ROWS)):
        if board[row][col] == 0:
            board[row][col] = piece
            return True
    return False

def check_win(board, piece):
    """Check if the given piece (1 or 2) has four in a row."""
    # Check horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    # Check vertical
    for c in range(COLS):
        for r in range(ROWS-3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    # Check diagonal /
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    # Check diagonal \
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    return False

def check_draw(board):
    """Check if the board is full (no empty spaces in top row)."""
    return all(board[0][c] != 0 for c in range(COLS))

def print_pretty_board(board):
    """
    Print the board in a human-friendly way:
    - X = Human (1)
    - O = AI (2)
    - . = empty
    Columns are numbered 0-6
    """
    print("0 1 2 3 4 5 6")  # column headers
    for row in board:
        row_str = ""
        for cell in row:
            if cell == 1:
                row_str += "X "
            elif cell == 2:
                row_str += "O "
            else:
                row_str += ". "
        print(row_str)
    print("\n")
