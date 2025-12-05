# ai.py
# This file implements the AI for Connect Four using Minimax and alpha-beta pruning.

import math
import random
import time
from board import ROWS, COLS, make_move, get_valid_moves, check_win, check_draw

# global counters
nodes_expanded = 0


def evaluate_window(window, piece):
    """
    Evaluate a 4-cell window.
    Positive score for AI piece, negative if opponent is threatening.
    """
    score = 0
    opp_piece = 1 if piece == 2 else 2

    # Count pieces in window
    count_piece = window.count(piece)
    count_opp = window.count(opp_piece)
    count_empty = window.count(0)

    # Scoring for AI
    if count_piece == 4:
        score += 1000  # Winning move
    elif count_piece == 3 and count_empty == 1:
        score += 10  # Potential 4-in-a-row
    elif count_piece == 2 and count_empty == 2:
        score += 5   # Less strong

    # Penalize opponent threats
    if count_opp == 3 and count_empty == 1:
        score -= 80   # High penalty for opponent about to win
    elif count_opp == 2 and count_empty == 2:
        score -= 5    # Minor penalty

    # Extra reward for double-threats (two AI pieces + two empty in multiple directions)
    if count_piece == 2 and count_empty == 2 and count_opp == 0:
        score += 2  # Encourages creating multiple threats

    return score

def score_position(board, piece):
    """
    Score the board for a given piece.
    """
    score = 0
    
    # center column priority
    center_array = [board[r][3] for r in range(6)]
    score += center_array.count(piece) * 6
    
    # Horizontal
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # Vertical
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # Positive diagonal (/)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Negative diagonal (\)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def minimax(board, depth, alpha, beta, maximizingPlayer, piece):
    """
    Minimax algorithm with alpha-beta pruning.
    Returns (best_col, best_score)
    """
    global nodes_expanded
    nodes_expanded += 1
    
    valid_moves = get_valid_moves(board)
    WIN_SCORE = 10000000
    LOSS_SCORE = -1000000
    
    # terminal check
    if check_win(board, piece):
          return (None, WIN_SCORE - (6 - depth))
    if check_win(board, 1 if piece == 2 else 2):
        return (None, LOSS_SCORE + (6 - depth))
    if check_draw(board):
        return (None, 0)
    if depth == 0:
        return (None, score_position(board, piece))

    if maximizingPlayer:
        value = -math.inf
        best_move = valid_moves[0]

        for col in valid_moves:
            temp_b = [row[:] for row in board]
            make_move(temp_b, col, piece)
            new_score = minimax(temp_b, depth - 1, alpha, beta, False, piece)[1]

            if new_score > value:
                value = new_score
                best_move = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return best_move, value

    else:
        value = math.inf
        opp_piece = 1 if piece == 2 else 2
        best_move = valid_moves[0]

        for col in valid_moves:
            temp_b = [row[:] for row in board]
            make_move(temp_b, col, opp_piece)
            new_score = minimax(temp_b, depth - 1, alpha, beta, True, piece)[1]

            if new_score < value:
                value = new_score
                best_move = col

            beta = min(beta, value)
            if beta <= alpha:
                break

        return best_move, value

def pick_best_move(board, piece, depth=4):
    """
    Returns the best column for AI to move.
    Default depth=4 (medium difficulty)
    """
    
    #col, _ = minimax(board, depth, -math.inf, math.inf, True, piece)
    #return col
    
    global nodes_expanded
    nodes_expanded = 0
    
    start = time.time()
    move, _ = minimax(board, depth, -math.inf, math.inf, True, piece)
    end = time.time()
    
    time_taken = end - start
    return move, time_taken, nodes_expanded



def random_move(board_state):
    """Return a random valid column (easy difficulty)."""
    valid_moves = get_valid_moves(board_state)
    return random.choice(valid_moves)
