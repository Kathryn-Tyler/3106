# test_ai.py
# Test AI move selection on example boards

from board import create_board, print_board, make_move
from ai import pick_best_move

# Create a test board
board = create_board()

# Simulate human moves
make_move(board, 0, 1)
make_move(board, 1, 1)
make_move(board, 2, 1)

print("Current board (before AI move):")
print_board(board)

# AI chooses the best move
ai_move = pick_best_move(board, 2, depth=3)
print("AI chooses column:", ai_move)

# Apply AI move to the board
make_move(board, ai_move, 2)

print("Board after AI move:")
print_board(board)
