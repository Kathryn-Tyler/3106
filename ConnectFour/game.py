# game.py
# Main game loop for human vs AI Connect Four in console

# from board import create_board, print_board, make_move, check_win, check_draw, get_valid_moves
import board
from ai import pick_best_move, random_move

def play_game():
    """Interactive Connect Four game between human (1) and AI (2)"""
    game_board = board.create_board()
    game_over = False
    turn = 0  # 0 = human, 1 = AI

    print("Welcome to Connect Four!")
    print("Choose difficulty:")
    print("1 = Easy (random moves)")
    print("2 = Medium (minimax depth 2)")
    print("3 = Hard (minimax depth 4)")
    
    # Difficulty selection loop
    while True:
        try:
            difficulty = int(input("Enter difficulty (1-3): "))
            if difficulty in [1, 2, 3]:
                break
            print("Invalid selection. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Enter a number between 1 and 3.")
            
    board.print_pretty_board(game_board)

    while not game_over:
        if turn == 0:  # Human turn
            valid_move = False
            while not valid_move:
                try:
                    col = int(input("Enter your move (0-6): "))
                    if col in board.get_valid_moves(game_board):
                        board.make_move(game_board, col, 1)
                        valid_move = True
                    else:
                        print("Column full or invalid. Try again.")
                except ValueError:
                    print("Invalid input. Enter a number 0-6.")

            if board.check_win(game_board, 1):
                board.print_pretty_board(game_board)
                print("Congratulations! You win!")
                game_over = True
            elif board.check_draw(game_board):
                board.print_pretty_board(game_board)
                print("It's a draw!")
                game_over = True

        else:  # AI turn
            print("AI is thinking...")

            # Difficulty-based decision-making
            if difficulty == 1:
                  # EASY = random legal move
                  col = random_move(game_board)
                  ai_time = 0
                  ai_nodes = 0

            elif difficulty == 2:
                  # MEDIUM = minimax depth 2
                  col, ai_time, ai_nodes = pick_best_move(game_board, 2, depth=2)

            else:
                  # HARD = minimax depth 4
                  col, ai_time, ai_nodes = pick_best_move(game_board, 2, depth=4)


            board.make_move(game_board, col, 2)
            print(f"AI chooses column {col}")
            
            if difficulty != 1:  # only for minimax AI
                  print(f"AI time: {ai_time:.8f} sec")
                  print(f"Nodes expanded: {ai_nodes}")
                  
             # Log AI performance to a file
                  with open("ai_performance_log.txt", "a") as f:
                        f.write(f"Difficulty {difficulty} | AI column {col} | Time {ai_time:.4f} | Nodes {ai_nodes}\n") 

            if board.check_win(game_board, 2):
                board.print_pretty_board(game_board)
                print("AI wins! Better luck next time.")
                game_over = True
            elif board.check_draw(game_board):
                board.print_pretty_board(game_board)
                print("It's a draw!")
                game_over = True

        board.print_pretty_board(game_board)
        turn = (turn + 1) % 2  # Switch turns

if __name__ == "__main__":
    play_game()
