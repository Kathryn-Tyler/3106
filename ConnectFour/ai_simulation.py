import board
from ai import pick_best_move, random_move
import time
import csv

def ai_vs_ai_game(depth1=2, depth2=4):
    game_board = board.create_board()
    turn = 0  # 0 = AI1, 1 = AI2
    move_log = []
    
    while True:
        valid_moves = board.get_valid_moves(game_board)
        if not valid_moves or board.check_win(game_board, 1) or board.check_win(game_board, 2):
            break

        if turn == 0:  # AI1
            col, ai_time, nodes = pick_best_move(game_board, 1, depth=depth1)
            board.make_move(game_board, col, 1)
            move_log.append((turn, col, ai_time, nodes))
        else:  # AI2
            col, ai_time, nodes = pick_best_move(game_board, 2, depth=depth2)
            board.make_move(game_board, col, 2)
            move_log.append((turn, col, ai_time, nodes))
        
        turn = (turn + 1) % 2
    
    winner = 0
    if board.check_win(game_board, 1):
        winner = 1
    elif board.check_win(game_board, 2):
        winner = 2

    return move_log, winner

# Run multiple games and save to CSV
def run_simulation(num_games=10):
    with open("ai_log.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Game", "MoveNum", "AI", "Column", "Time", "Nodes", "Winner"])
        for g in range(num_games):
            moves, winner = ai_vs_ai_game()
            for i, (ai, col, t, nodes) in enumerate(moves):
                writer.writerow([g+1, i+1, ai, col, round(t,6), nodes, winner])

if __name__ == "__main__":
    run_simulation()
    print("Simulation complete. Logs saved to ai_log.csv")
