# midgame_test.py
# Evaluation of Depth-1 (easy) AI against Depth-2 and Depth-4
# Includes graphical analysis of win rates and move times
# Added terminal logging for live progress and final summary

import csv
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd

from board import ROWS, COLS, create_board, make_move, get_valid_moves, check_win, check_draw
from ai import pick_best_move

REPEATS = 20  # number of games per position/matchup

POSITIONS = [
    # Midgame fork scenario for X
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
    # Midgame diagonal potential for O
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
    # Midgame vertical threat
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
    # Midgame balanced board, no immediate wins
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
    # Empty starting board
    {
        "name": "E_empty_start",
        "board": [
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0]
        ],
        "next_to_move": 1
    },
    # Nearly full board, testing draw scenarios
    {
        "name": "F_nearly_full",
        "board": [
            [1,2,1,2,1,2,1],
            [2,1,2,1,2,1,2],
            [1,2,1,2,1,2,1],
            [2,1,2,1,2,1,2],
            [1,2,1,2,1,2,1],
            [2,1,2,1,2,1,0]
        ],
        "next_to_move": 2
    }
]

# Matchups include Depth-1 comparisons
MATCHUPS = [
    (1, 2, "Depth-1 vs Depth-2"),
    (1, 4, "Depth-1 vs Depth-4"),
    (2, 4, "Depth-2 vs Depth-4"),
    (1, 1, "Depth-1 vs Depth-1"),
    (2, 2, "Depth-2 vs Depth-2"),
    (4, 4, "Depth-4 vs Depth-4"),
]

def play_from_position(start_board, start_player, p1_depth, p2_depth):
    """Plays a full game from a starting position."""
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

def log_game_progress(pos_name, matchup_label, start_player, game_num, total_games, winner_label, moves, depth1_summary=None):
    """Prints live progress of each game to the terminal."""
    print(f"\nPosition: {pos_name} | Matchup: {matchup_label} | Starting Player: {start_player}")
    print(f"  Game {game_num}/{total_games} finished. Winner: {winner_label}. Moves: {moves}")
    
    # Optional Depth-1 summary after each game
    if depth1_summary:
        d1_stats = ", ".join([f"{k}: {v['wins']}W/{v['losses']}L/{v['draws']}D" for k,v in depth1_summary.items()])
        print(f"  Depth-1 cumulative: {d1_stats}")

def print_depth1_summary(summary):
    """Prints a final cumulative Depth-1 summary in the terminal."""
    print("\n===== FINAL DEPTH-1 SUMMARY =====")
    for matchup, stats in summary.items():
        total_games = stats['wins'] + stats['losses'] + stats['draws']
        avg_time = sum(stats['times'])/len(stats['times']) if stats['times'] else 0
        print(f"{matchup}: {stats['wins']}W / {stats['losses']}L / {stats['draws']}D | Total Games: {total_games} | Avg Move Time: {avg_time:.3f}s")

def run_all_tests(out_csv="midgame_results.csv"):
    rows = []
    header = [
        "Position", "Matchup", "Starting Player", "Winner", "Total Moves",
        "Avg Time Player 1 (s)", "Avg Nodes Player 1",
        "Avg Time Player 2 (s)", "Avg Nodes Player 2"
    ]

    # Overall tracking
    depth1_summary = {
        "D1_vs_D2": {"wins":0, "losses":0, "draws":0, "times":[]},
        "D1_vs_D4": {"wins":0, "losses":0, "draws":0, "times":[]}
    }

    for pos in POSITIONS:
        name = pos["name"]
        board = pos["board"]

        for p1_depth, p2_depth, label in MATCHUPS:
            for start_player in (pos["next_to_move"], 3 - pos["next_to_move"]):
                t1, t2, n1, n2, winners = [], [], [], [], []

                for game_num in range(REPEATS):
                    winner, moves, times, nodes = play_from_position(board, start_player, p1_depth, p2_depth)
                    winners.append(winner)
                    t1.extend(times[1])
                    t2.extend(times[2])
                    n1.extend(nodes[1])
                    n2.extend(nodes[2])

                    result = Counter(winners).most_common(1)[0][0]
                    winner_label = "Draw" if result==0 else f"Player {result} (Depth-{p1_depth if result==1 else p2_depth})"

                    # Log progress
                    log_game_progress(
                        pos_name=name,
                        matchup_label=label,
                        start_player=start_player,
                        game_num=game_num+1,
                        total_games=REPEATS,
                        winner_label=winner_label,
                        moves=moves,
                        depth1_summary=depth1_summary
                    )

                # Depth-1 comparisons
                if (p1_depth == 1 and p2_depth == 2) or (p1_depth == 2 and p2_depth == 1):
                    depth1_times = t1 if p1_depth==1 else t2
                    depth1_summary["D1_vs_D2"]["times"].extend(depth1_times)
                    if (result == 1 and p1_depth==1) or (result==2 and p2_depth==1):
                        depth1_summary["D1_vs_D2"]["wins"] += 1
                    elif result == 0:
                        depth1_summary["D1_vs_D2"]["draws"] += 1
                    else:
                        depth1_summary["D1_vs_D2"]["losses"] += 1

                if (p1_depth == 1 and p2_depth == 4) or (p1_depth == 4 and p2_depth == 1):
                    depth1_times = t1 if p1_depth==1 else t2
                    depth1_summary["D1_vs_D4"]["times"].extend(depth1_times)
                    if (result == 1 and p1_depth==1) or (result==2 and p2_depth==1):
                        depth1_summary["D1_vs_D4"]["wins"] += 1
                    elif result == 0:
                        depth1_summary["D1_vs_D4"]["draws"] += 1
                    else:
                        depth1_summary["D1_vs_D4"]["losses"] += 1

                avg_t1 = sum(t1)/len(t1) if t1 else 0
                avg_t2 = sum(t2)/len(t2) if t2 else 0
                avg_n1 = sum(n1)/len(n1) if n1 else 0
                avg_n2 = sum(n2)/len(n2) if n2 else 0

                start_label = f"Player {start_player} (Depth-{p1_depth if start_player==1 else p2_depth})"

                rows.append([
                    name, label, start_label, winner_label, sum([len(t1),len(t2)]),
                    avg_t1, avg_n1, avg_t2, avg_n2
                ])

    # Save CSV
    df = pd.DataFrame(rows, columns=header)
    df.to_csv(out_csv, index=False)
    print(f"\nResults saved to {out_csv}")

    # Print final cumulative Depth-1 summary
    print_depth1_summary(depth1_summary)
    
    # ===== PLOTS =====
    plot_depth1_winrates(depth1_summary)
    plot_depth1_times(depth1_summary)


def plot_depth1_winrates(summary):
    """Bar chart: Depth-1 wins/losses/draws vs Depth-2 and Depth-4"""
    import matplotlib.pyplot as plt
    import numpy as np

    categories = ["D1_vs_D2", "D1_vs_D4"]
    wins = [summary[c]["wins"] for c in categories]
    losses = [summary[c]["losses"] for c in categories]
    draws = [summary[c]["draws"] for c in categories]

    x = np.arange(len(categories))
    width = 0.3

    plt.figure(figsize=(8,5))
    plt.bar(x - width, wins, width, label="Wins", color="green")
    plt.bar(x, draws, width, label="Draws", color="gray")
    plt.bar(x + width, losses, width, label="Losses", color="red")
    plt.xticks(x, ["Depth-1 vs Depth-2", "Depth-1 vs Depth-4"])
    plt.ylabel("Number of Games")
    plt.title("Depth-1 Win/Loss/Draw Performance")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_depth1_times(summary):
    """Bar chart: average move time per turn for Depth-1 vs Depth-2/Depth-4"""
    import matplotlib.pyplot as plt
    import numpy as np

    categories = ["D1_vs_D2", "D1_vs_D4"]
    avg_times = [sum(summary[c]["times"])/len(summary[c]["times"]) if summary[c]["times"] else 0 for c in categories]

    plt.figure(figsize=(6,4))
    plt.bar(["Depth-1 vs Depth-2", "Depth-1 vs Depth-4"], avg_times, color="blue")
    plt.ylabel("Average Move Time (s)")
    plt.title("Depth-1 Average Move Time Comparison")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_all_tests()
