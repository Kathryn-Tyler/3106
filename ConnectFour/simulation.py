# simulation.py
# Automated simulation and analysis for Connect Four AI

import random
from board import create_board, make_move, get_valid_moves, check_win, check_draw
from ai import pick_best_move, random_move, score_position

NUM_GAMES = 4  # number of games per matchup
DIFFICULTIES = {
    2: "Medium (depth=2)",
    4: "Hard (depth=4)"
}

def simulate_game(ai1_depth=None, ai2_depth=None, opponent_type="random", ai1_starts=True):
    """
    Simulate one game:
    - If ai1_depth and ai2_depth are provided => AI vs AI
    - Otherwise AI vs opponent_type
    Returns stats: winner, avg_time_ai1, avg_nodes_ai1, avg_time_ai2, avg_nodes_ai2
    """
    board = create_board()
    turn = 0 if ai1_starts else 1  # alternate first player
    times_ai1, nodes_ai1 = [], []
    times_ai2, nodes_ai2 = [], []

    while not check_win(board, 1) and not check_win(board, 2) and not check_draw(board):
        if turn == 0:
            # AI1 move
            col, time_taken, nodes_expanded = pick_best_move(board, 2, depth=ai1_depth) if ai1_depth else pick_best_move(board, 2, depth=2)
            make_move(board, col, 2)
            times_ai1.append(time_taken)
            nodes_ai1.append(nodes_expanded)
        else:
            # AI2 or opponent move
            if ai2_depth:
                col, time_taken, nodes_expanded = pick_best_move(board, 1, depth=ai2_depth)
                make_move(board, col, 1)
                times_ai2.append(time_taken)
                nodes_ai2.append(nodes_expanded)
            else:
                col = random_move(board) if opponent_type == "random" else pick_best_move(board, 1, depth=2)[0]
                make_move(board, col, 1)
        turn = (turn + 1) % 2

    # Determine winner
    if check_win(board, 2):
        winner = "AI1"
    elif check_win(board, 1):
        winner = "AI2" if ai2_depth else "Opponent"
    else:
        winner = "Draw"

    avg_time_ai1 = sum(times_ai1)/len(times_ai1) if times_ai1 else 0
    avg_nodes_ai1 = sum(nodes_ai1)/len(nodes_ai1) if nodes_ai1 else 0
    avg_time_ai2 = sum(times_ai2)/len(times_ai2) if times_ai2 else 0
    avg_nodes_ai2 = sum(nodes_ai2)/len(nodes_ai2) if nodes_ai2 else 0

    return winner, avg_time_ai1, avg_nodes_ai1, avg_time_ai2, avg_nodes_ai2

def run_simulation():
    results = []

    # AI vs Random
    for depth, name in DIFFICULTIES.items():
        print(f"Simulating {NUM_GAMES} games: {name} vs Random")
        wins = {"AI1": 0, "Opponent": 0, "Draw": 0}
        total_time_ai1 = total_nodes_ai1 = 0

        for i in range(NUM_GAMES):
            # Alternate first player to remove bias
            ai1_starts = (i % 2 == 0)
            winner, avg_time_ai1, avg_nodes_ai1, _, _ = simulate_game(ai1_depth=depth, ai1_starts=ai1_starts)
            wins[winner] += 1
            total_time_ai1 += avg_time_ai1
            total_nodes_ai1 += avg_nodes_ai1

        results.append({
            "matchup": f"{name} vs Random",
            "win_rate": wins["AI1"]/NUM_GAMES,
            "loss_rate": wins["Opponent"]/NUM_GAMES,
            "draw_rate": wins["Draw"]/NUM_GAMES,
            "avg_time": total_time_ai1/NUM_GAMES,
            "avg_nodes": total_nodes_ai1/NUM_GAMES
        })

    # AI vs AI: same level, level above, level below
    depths = sorted(DIFFICULTIES.keys())
    for i, depth in enumerate(depths):
        opponents = [depth]
        if i > 0:
            opponents.append(depths[i-1])
        if i < len(depths)-1:
            opponents.append(depths[i+1])

        for opp_depth in opponents:
            if depth == opp_depth:
                matchup_name = f"{DIFFICULTIES[depth]} vs {DIFFICULTIES[opp_depth]} (same level)"
            else:
                matchup_name = f"{DIFFICULTIES[depth]} vs {DIFFICULTIES[opp_depth]}"

            print(f"Simulating {NUM_GAMES} games: {matchup_name}")
            wins = {"AI1": 0, "AI2": 0, "Draw": 0}
            total_time_ai1 = total_nodes_ai1 = 0
            total_time_ai2 = total_nodes_ai2 = 0

            for j in range(NUM_GAMES):
                # Alternate first player
                ai1_starts = (j % 2 == 0)
                winner, avg_time_ai1, avg_nodes_ai1, avg_time_ai2, avg_nodes_ai2 = simulate_game(ai1_depth=depth, ai2_depth=opp_depth, ai1_starts=ai1_starts)
                wins[winner] += 1
                total_time_ai1 += avg_time_ai1
                total_nodes_ai1 += avg_nodes_ai1
                total_time_ai2 += avg_time_ai2
                total_nodes_ai2 += avg_nodes_ai2

            results.append({
                "matchup": matchup_name,
                "win_rate_ai1": wins["AI1"]/NUM_GAMES,
                "win_rate_ai2": wins["AI2"]/NUM_GAMES,
                "draw_rate": wins["Draw"]/NUM_GAMES,
                "avg_time_ai1": total_time_ai1/NUM_GAMES,
                "avg_nodes_ai1": total_nodes_ai1/NUM_GAMES,
                "avg_time_ai2": total_time_ai2/NUM_GAMES,
                "avg_nodes_ai2": total_nodes_ai2/NUM_GAMES
            })

    # Print summary
    print("\n=== Simulation Summary ===")
    for r in results:
        print(f"{r['matchup']}:")
        if 'win_rate' in r:  # AI vs Random
            print(f"  Win rate: {r['win_rate']*100:.1f}%")
            print(f"  Loss rate: {r['loss_rate']*100:.1f}%")
            print(f"  Draw rate: {r['draw_rate']*100:.1f}%")
            print(f"  Avg time per move: {r['avg_time']:.4f}s")
            print(f"  Avg nodes expanded per move: {r['avg_nodes']:.1f}\n")
        else:  # AI vs AI
            print(f"  Win rate AI1: {r['win_rate_ai1']*100:.1f}%")
            print(f"  Win rate AI2: {r['win_rate_ai2']*100:.1f}%")
            print(f"  Draw rate: {r['draw_rate']*100:.1f}%")
            print(f"  Avg time AI1: {r['avg_time_ai1']:.4f}s")
            print(f"  Avg nodes AI1: {r['avg_nodes_ai1']:.1f}")
            print(f"  Avg time AI2: {r['avg_time_ai2']:.4f}s")
            print(f"  Avg nodes AI2: {r['avg_nodes_ai2']:.1f}\n")

if __name__ == "__main__":
    run_simulation()
