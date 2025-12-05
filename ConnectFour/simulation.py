# simulation.py
# Automated simulation and analysis for Connect Four AI (AI vs AI only)

from board import create_board, make_move, get_valid_moves, check_win, check_draw
from ai import pick_best_move

NUM_GAMES = 4  # number of games per matchup
DIFFICULTIES = {
    1: "Easy (depth=1)",
    2: "Medium (depth=2)",
    4: "Hard (depth=4)"
}

def simulate_game(ai1_depth, ai2_depth, ai1_starts=True):
    """
    Simulate one game: AI1 vs AI2
    Returns: winner, avg_time_ai1, avg_nodes_ai1, avg_time_ai2, avg_nodes_ai2
    """
    board = create_board()
    turn = 0 if ai1_starts else 1  # 0 = AI1, 1 = AI2
    times_ai1, nodes_ai1 = [], []
    times_ai2, nodes_ai2 = [], []

    while not check_win(board, 1) and not check_win(board, 2) and not check_draw(board):
        if turn == 0:
            col, time_taken, nodes_expanded = pick_best_move(board, 1, depth=ai1_depth)
            make_move(board, col, 1)
            times_ai1.append(time_taken)
            nodes_ai1.append(nodes_expanded)
        else:
            col, time_taken, nodes_expanded = pick_best_move(board, 2, depth=ai2_depth)
            make_move(board, col, 2)
            times_ai2.append(time_taken)
            nodes_ai2.append(nodes_expanded)
        turn = 1 - turn

    if check_win(board, 1):
        winner = "AI1"
    elif check_win(board, 2):
        winner = "AI2"
    else:
        winner = "Draw"

    avg_time_ai1 = sum(times_ai1)/len(times_ai1) if times_ai1 else 0
    avg_nodes_ai1 = sum(nodes_ai1)/len(nodes_ai1) if nodes_ai1 else 0
    avg_time_ai2 = sum(times_ai2)/len(times_ai2) if times_ai2 else 0
    avg_nodes_ai2 = sum(nodes_ai2)/len(nodes_ai2) if nodes_ai2 else 0

    return winner, avg_time_ai1, avg_nodes_ai1, avg_time_ai2, avg_nodes_ai2


def run_simulation():
    results = []
    depths = sorted(DIFFICULTIES.keys())

    # AI vs AI: all depth combinations
    for i, depth1 in enumerate(depths):
        for j, depth2 in enumerate(depths):
            matchup_name = f"{DIFFICULTIES[depth1]} vs {DIFFICULTIES[depth2]}"
            print(f"Simulating {NUM_GAMES} games: {matchup_name}")

            wins = {"AI1": 0, "AI2": 0, "Draw": 0}
            total_time_ai1 = total_nodes_ai1 = 0
            total_time_ai2 = total_nodes_ai2 = 0

            for k in range(NUM_GAMES):
                ai1_starts = (k % 2 == 0)
                winner, avg_time_ai1, avg_nodes_ai1, avg_time_ai2, avg_nodes_ai2 = simulate_game(
                    ai1_depth=depth1, ai2_depth=depth2, ai1_starts=ai1_starts
                )
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
        print(f"  Win rate AI1: {r['win_rate_ai1']*100:.1f}%")
        print(f"  Win rate AI2: {r['win_rate_ai2']*100:.1f}%")
        print(f"  Draw rate: {r['draw_rate']*100:.1f}%")
        print(f"  Avg time AI1: {r['avg_time_ai1']:.4f}s")
        print(f"  Avg nodes AI1: {r['avg_nodes_ai1']:.1f}")
        print(f"  Avg time AI2: {r['avg_time_ai2']:.4f}s")
        print(f"  Avg nodes AI2: {r['avg_nodes_ai2']:.1f}\n")


if __name__ == "__main__":
    run_simulation()
