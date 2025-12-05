# midgame_test.py
# Run controlled mid-game experiments comparing depth-2 and depth-4 AIs.
# Outputs a CSV and prints a results table.

import csv
import copy
import time
from collections import Counter
from board import ROWS, COLS, create_board, make_move, get_valid_moves, check_win, check_draw
from ai import pick_best_move, random_move

# Number of repeated runs per setting (deterministic AIs => results will be same,
# but we run twice swapping who is 'player1' to remove first-move bias)
REPEATS = 2

# Define positions: each entry is dict with 'name', 'board' (6x7 ints), and 'next_to_move' (1 or 2)
POSITIONS = [
    {
        "name": "A_fork_X",
        "board": [
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,1,2,0,0],
            [0,1,1,2,2,0,0],
            [1,2,2,1,1,0,0]
        ],
        "next_to_move": 2
    },
    {
        "name": "B_diag_O",
        "board": [
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,1,0,0],
            [0,0,2,1,2,0,0],
            [0,1,2,2,1,0,0],
            [1,2,1,1,2,0,0]
        ],
        "next_to_move": 1
    },
    {
        "name": "C_vertical",
        "board": [
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,2,1,0,0,0],
            [0,0,1,2,2,0,0],
            [1,1,2,1,1,0,0]
        ],
        "next_to_move": 2
    },
    {
        "name": "D_balanced",
        "board": [
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,2,0,0,0],
            [0,1,2,1,0,0,0],
            [0,2,1,2,1,0,0],
            [1,1,2,1,2,0,0]
        ],
        "next_to_move": 1
    },
    # Add 4 more positions here or reuse these if you prefer fewer tests.
]

# Matchup configurations to run for each position
# Each entry: (p1_depth, p2_depth, label)
# Use None for random (easy)
MATCHUPS = [
    (2, 4, "Depth2_vs_Depth4"),
    (4, 2, "Depth4_vs_Depth2"),
    (2, 2, "Depth2_vs_Depth2"),
    (4, 4, "Depth4_vs_Depth4"),
]

# Play from a given board until terminal with specified depths per player.
# p1_depth = None means random opponent.
def play_from_position(start_board, start_player, p1_depth, p2_depth):
    board = [row[:] for row in start_board]
    current = start_player  # 1 or 2
    history = []
    times = {1: [], 2: []}
    nodes = {1: [], 2: []}

    while True:
        if check_win(board, 1) or check_win(board, 2) or check_draw(board):
            break

        if current == 1:
            depth = p1_depth
            piece = 1
        else:
            depth = p2_depth
            piece = 2

        if depth is None:
            # random move
            col = random_move(board)
            t = 0.0
            n = 0
        else:
            start = time.time()
            move, t_taken, n_expanded = pick_best_move(board, piece, depth=depth)
            t = t_taken
            n = n_expanded
            col = move

        # Safety: if move is invalid (e.g., pick_best_move returned None), pick random valid
        if col not in get_valid_moves(board):
            col = random_move(board)

        make_move(board, col, piece)
        history.append((current, col))
        times[current].append(t)
        nodes[current].append(n)

        current = 1 if current == 2 else 2

    # outcome
    if check_win(board, 1):
        winner = 1
    elif check_win(board, 2):
        winner = 2
    else:
        winner = 0  # draw

    return winner, history, times, nodes

def run_all_tests(out_csv="midgame_results.csv"):
    rows = []
    header = ["position", "matchup", "start_player", "winner", "moves", "avg_time_p1", "avg_nodes_p1", "avg_time_p2", "avg_nodes_p2"]
    for pos in POSITIONS:
        name = pos["name"]
        start_board = pos["board"]
        # For each matchup, run with both possible starting players (to remove first-move bias)
        for p1_depth, p2_depth, label in MATCHUPS:
            for start_player in (pos["next_to_move"], 1 if pos["next_to_move"]==2 else 2):
                # run REPEATS times (deterministic AIs => same result normally)
                winners = []
                accum = {"p1_time": [], "p2_time": [], "p1_nodes": [], "p2_nodes": []}
                for r in range(REPEATS):
                    winner, history, times, nodes = play_from_position(start_board, start_player, p1_depth, p2_depth)
                    winners.append(winner)
                    accum["p1_time"].extend(times[1])
                    accum["p2_time"].extend(times[2])
                    accum["p1_nodes"].extend(nodes[1])
                    accum["p2_nodes"].extend(nodes[2])

                # majority winner (or draw if mixed)
                winner_count = Counter(winners)
                # map winner int to label
                if winner_count:
                    most_common = winner_count.most_common(1)[0][0]
                else:
                    most_common = 0
                if most_common == 1:
                    winner_label = "P1"
                elif most_common == 2:
                    winner_label = "P2"
                else:
                    winner_label = "Draw"

                avg_p1_time = sum(accum["p1_time"])/len(accum["p1_time"]) if accum["p1_time"] else 0
                avg_p2_time = sum(accum["p2_time"])/len(accum["p2_time"]) if accum["p2_time"] else 0
                avg_p1_nodes = sum(accum["p1_nodes"])/len(accum["p1_nodes"]) if accum["p1_nodes"] else 0
                avg_p2_nodes = sum(accum["p2_nodes"])/len(accum["p2_nodes"]) if accum["p2_nodes"] else 0

                rows.append([
                    name, label, start_player, winner_label, len(history),
                    f"{avg_p1_time:.6f}", f"{avg_p1_nodes:.1f}", f"{avg_p2_time:.6f}", f"{avg_p2_nodes:.1f}"
                ])
                print(f"[{name}] {label} start:{start_player} -> winner {winner_label} moves {len(history)} p1_t {avg_p1_time:.6f} p2_t {avg_p2_time:.6f}")

    # write CSV
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print("Saved results to", out_csv)

if __name__ == "__main__":
    run_all_tests()
