'''# midgame_test.py
# Clean deterministic evaluation of depth-2 vs depth-4 AIs
# against fixed midgame positions.

import csv
import time
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd

from board import ROWS, COLS, create_board, make_move, get_valid_moves, check_win, check_draw
from ai import pick_best_move

# Since minimax is deterministic, repeating once is enough
REPEATS = 1

# -----------------------------
# Test Positions
# -----------------------------
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
    }
]

# Matchups: (P1_depth, P2_depth, Name)
MATCHUPS = [
    (2, 4, "Depth2_vs_Depth4"),
    (4, 2, "Depth4_vs_Depth2"),
    (2, 2, "Depth2_vs_Depth2"),
    (4, 4, "Depth4_vs_Depth4"),
]

# ----------------------------------------
# Play one full game from a given position
# ----------------------------------------
def play_from_position(start_board, start_player, p1_depth, p2_depth):
    board = [row[:] for row in start_board]
    current = start_player
    times = {1: [], 2: []}
    nodes = {1: [], 2: []}
    move_count = 0

    while True:
        if check_win(board, 1) or check_win(board, 2) or check_draw(board):
            break

        depth = p1_depth if current == 1 else p2_depth
        piece = current

        # AI move
        try:
            move, t_taken, n_expanded = pick_best_move(board, piece, depth=depth)
        except:
            # Fallback if AI fails
            move = None
            t_taken = 0
            n_expanded = 0

        # Store analytics
        times[current].append(t_taken)
        nodes[current].append(n_expanded)

        valid_moves = get_valid_moves(board)
        if move not in valid_moves:
            move = valid_moves[0]  # safe fallback

        make_move(board, move, piece)
        move_count += 1
        current = 1 if current == 2 else 2

    # winner
    if check_win(board, 1):
        return 1, move_count, times, nodes
    elif check_win(board, 2):
        return 2, move_count, times, nodes
    else:
        return 0, move_count, times, nodes


# ----------------------------------------
# Run all matchups and positions
# ----------------------------------------
def run_all_tests(out_csv="midgame_results.csv"):
    rows = []
    header = [
        "position", "matchup", "start_player", "winner", "moves",
        "avg_time_p1", "avg_nodes_p1", "avg_time_p2", "avg_nodes_p2"
    ]

    # Track wins across everything
    overall = {"D2": 0, "D4": 0, "Draw": 0}

    for pos in POSITIONS:
        name = pos["name"]
        board = pos["board"]

        for p1_depth, p2_depth, label in MATCHUPS:
            # Test both possible starting players
            for start_player in (pos["next_to_move"], 1 if pos["next_to_move"] == 2 else 2):

                winners = []
                t1 = []
                t2 = []
                n1 = []
                n2 = []

                for _ in range(REPEATS):
                    winner, moves, times, nodes = play_from_position(board, start_player, p1_depth, p2_depth)
                    winners.append(winner)
                    t1.extend(times[1])
                    t2.extend(times[2])
                    n1.extend(nodes[1])
                    n2.extend(nodes[2])

                # Pick the most common outcome
                result = Counter(winners).most_common(1)[0][0]

                if result == 1:
                    winner_label = "P1"
                    overall["D2" if p1_depth == 2 else "D4"] += 1
                elif result == 2:
                    winner_label = "P2"
                    overall["D2" if p2_depth == 2 else "D4"] += 1
                else:
                    winner_label = "Draw"
                    overall["Draw"] += 1

                avg_t1 = sum(t1)/len(t1) if t1 else 0
                avg_t2 = sum(t2)/len(t2) if t2 else 0
                avg_n1 = sum(n1)/len(n1) if n1 else 0
                avg_n2 = sum(n2)/len(n2) if n2 else 0

                # Clean readable terminal output
                print(f"\n[{name}]  {label} | Start: {start_player} | Winner: {winner_label}")
                print(f"   Moves: {moves}")
                print(f"   P1 avg time:  {avg_t1:.6f}  | P1 nodes: {avg_n1:.1f}")
                print(f"   P2 avg time:  {avg_t2:.6f}  | P2 nodes: {avg_n2:.1f}")

                rows.append([
                    name, label, start_player, winner_label, moves,
                    avg_t1, avg_n1, avg_t2, avg_n2
                ])

    # Write CSV
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print("\nSaved CSV:", out_csv)

    # Final strength summary
    print("\n===== FINAL PERFORMANCE SUMMARY =====")
    print(f"Depth-2 wins: {overall['D2']}")
    print(f"Depth-4 wins: {overall['D4']}")
    print(f"Draws:        {overall['Draw']}")

    if overall["D4"] > overall["D2"]:
        print("Conclusion: Depth-4 is stronger overall.")
    elif overall["D2"] > overall["D4"]:
        print("Conclusion: Depth-2 surprisingly performed better.")
    else:
        print("Conclusion: They performed equally.")

    generate_plot(out_csv)


# ----------------------------------------
# Plot results
# ----------------------------------------
def generate_plot(csv_path):
    df = pd.read_csv(csv_path)

    plt.figure(figsize=(9,6))

    for label, group in df.groupby("matchup"):
        plt.plot(group["moves"], group["avg_nodes_p1"], marker="o", label=label)

    plt.title("Nodes Expanded (Player 1) by Matchup")
    plt.xlabel("Moves in Game")
    plt.ylabel("Avg Nodes Expanded")
    plt.legend()
    plt.tight_layout()
    plt.savefig("midgame_performance.png")
    print("Saved plot: midgame_performance.png")


if __name__ == "__main__":
    run_all_tests()
'''
# midgame_test.py
# Clean deterministic evaluation of depth-2 vs depth-4 AIs
# against fixed midgame positions.

import csv
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd

from board import ROWS, COLS, create_board, make_move, get_valid_moves, check_win, check_draw
from ai import pick_best_move

# Number of repeats for each test
REPEATS = 1

# -----------------------------
# Test Positions
# -----------------------------
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
    }
]

# Matchups: (P1_depth, P2_depth, Name)
MATCHUPS = [
    (2, 4, "Depth-2 vs Depth-4"),
    (4, 2, "Depth-4 vs Depth-2"),
    (2, 2, "Depth-2 vs Depth-2"),
    (4, 4, "Depth-4 vs Depth-4"),
]

# ----------------------------------------
# Play one full game from a given position
# ----------------------------------------
def play_from_position(start_board, start_player, p1_depth, p2_depth):
    board = [row[:] for row in start_board]
    current = start_player
    times = {1: [], 2: []}
    nodes = {1: [], 2: []}
    move_count = 0

    while True:
        if check_win(board, 1) or check_win(board, 2) or check_draw(board):
            break

        depth = p1_depth if current == 1 else p2_depth
        piece = current

        try:
            move, t_taken, n_expanded = pick_best_move(board, piece, depth=depth)
        except:
            move = None
            t_taken = 0
            n_expanded = 0

        times[current].append(t_taken)
        nodes[current].append(n_expanded)

        valid_moves = get_valid_moves(board)
        if move not in valid_moves:
            move = valid_moves[0]

        make_move(board, move, piece)
        move_count += 1
        current = 1 if current == 2 else 2

    if check_win(board, 1):
        return 1, move_count, times, nodes
    elif check_win(board, 2):
        return 2, move_count, times, nodes
    else:
        return 0, move_count, times, nodes

# ----------------------------------------
# Run all matchups and positions
# ----------------------------------------
def run_all_tests(out_csv="midgame_results.csv"):
    rows = []
    header = [
        "Position", "Matchup", "Starting Player", "Winner", "Total Moves",
        "Avg Time Player 1 (s)", "Avg Nodes Player 1",
        "Avg Time Player 2 (s)", "Avg Nodes Player 2"
    ]

    overall = {"Depth-2": 0, "Depth-4": 0, "Draw": 0}

    for pos in POSITIONS:
        name = pos["name"]
        board = pos["board"]

        for p1_depth, p2_depth, label in MATCHUPS:

            for start_player in (pos["next_to_move"], 3 - pos["next_to_move"]):

                t1, t2, n1, n2, winners = [], [], [], [], []

                for _ in range(REPEATS):
                    winner, moves, times, nodes = play_from_position(board, start_player, p1_depth, p2_depth)
                    winners.append(winner)
                    t1.extend(times[1])
                    t2.extend(times[2])
                    n1.extend(nodes[1])
                    n2.extend(nodes[2])

                result = Counter(winners).most_common(1)[0][0]

                if result == 1:
                    winner_label = f"Player 1 (Depth-{p1_depth})"
                    overall[f"Depth-{p1_depth}"] += 1
                elif result == 2:
                    winner_label = f"Player 2 (Depth-{p2_depth})"
                    overall[f"Depth-{p2_depth}"] += 1
                else:
                    winner_label = "Draw"
                    overall["Draw"] += 1

                avg_t1 = sum(t1)/len(t1) if t1 else 0
                avg_t2 = sum(t2)/len(t2) if t2 else 0
                avg_n1 = sum(n1)/len(n1) if n1 else 0
                avg_n2 = sum(n2)/len(n2) if n2 else 0

                start_label = f"Player {start_player} (Depth-{p1_depth if start_player == 1 else p2_depth})"

                print(f"\nPosition: {name}")
                print(f"Matchup: {label}")
                print(f"Starting Player: {start_label}")
                print(f"Winner: {winner_label}")
                print(f"Total Moves: {moves}")
                print(f"Player 1 -> Avg Time: {avg_t1:.6f}s | Avg Nodes: {avg_n1:.1f}")
                print(f"Player 2 -> Avg Time: {avg_t2:.6f}s | Avg Nodes: {avg_n2:.1f}")

                rows.append([
                    name, label, start_label, winner_label, moves,
                    avg_t1, avg_n1, avg_t2, avg_n2
                ])

    # Write CSV
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print("\nSaved CSV:", out_csv)

    print("\n===== FINAL PERFORMANCE SUMMARY =====")
    print(f"Depth-2 wins: {overall['Depth-2']}")
    print(f"Depth-4 wins: {overall['Depth-4']}")
    print(f"Draws:        {overall['Draw']}")

    if overall["Depth-4"] > overall["Depth-2"]:
        print("Conclusion: Depth-4 is stronger overall.")
    elif overall["Depth-2"] > overall["Depth-4"]:
        print("Conclusion: Depth-2 performed better.")
    else:
        print("Conclusion: Both depths performed equally.")

    generate_plot(out_csv)

# ----------------------------------------
# Plot results (interactive)
# ----------------------------------------
def generate_plot(csv_path):
    df = pd.read_csv(csv_path)
    plt.figure(figsize=(9,6))
    for label, group in df.groupby("Matchup"):
        plt.plot(group["Total Moves"], group["Avg Nodes Player 1"], marker="o", label=label)
    plt.title("Nodes Expanded by Player 1 per Matchup")
    plt.xlabel("Moves in Game")
    plt.ylabel("Average Nodes Expanded (Player 1)")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_all_tests()
