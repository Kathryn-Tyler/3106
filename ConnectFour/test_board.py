# test_board.py
# Quick tests for board.py to make sure game rules work

from board import create_board, print_board, make_move, check_win, check_draw

# Create an empty board
board = create_board()
print_board(board)

# Simulate some moves
make_move(board, 0, 1)  # Human
make_move(board, 0, 2)  # AI
make_move(board, 1, 1)
make_move(board, 1, 2)
make_move(board, 2, 1)
make_move(board, 2, 2)
make_move(board, 3, 1)  # Human winning move

print_board(board)

# Check win conditions
print("Win for Human (1)?", check_win(board, 1))
print("Win for AI (2)?", check_win(board, 2))
print("Draw?", check_draw(board))
