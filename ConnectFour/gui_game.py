import sys
import pygame
import board
from ai import pick_best_move

# --- GUI CONFIG ---
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)

WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT + 1) * SQUARESIZE  # Extra top row for user input
SIZE = (WIDTH, HEIGHT)

BLUE = (25, 25, 112)
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)   # Human
RED = (220, 20, 60)      # AI
WHITE = (255, 255, 255)

pygame.init()
FONT = pygame.font.SysFont("arial", 40, bold=True)
MENU_FONT = pygame.font.SysFont("arial", 50, bold=True)


# ----------------------------------------
# Draw the Connect Four Board
# ----------------------------------------
def draw_board(game_board, screen):
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):

            # Board background
            pygame.draw.rect(screen, BLUE,
                             (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE,
                              SQUARESIZE, SQUARESIZE))

            # Empty or filled slot
            piece = game_board[r][c]
            color = BLACK
            if piece == 1:
                color = YELLOW
            elif piece == 2:
                color = RED

            pygame.draw.circle(screen, color,
                               (c * SQUARESIZE + SQUARESIZE // 2,
                                r * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2),
                               RADIUS)
    pygame.display.update()


# ----------------------------------------
# Difficulty Menu Screen
# ----------------------------------------
def difficulty_menu(screen):
    screen.fill(BLUE)

    title = MENU_FONT.render("Select Difficulty", True, WHITE)
    easy = FONT.render("1. Easy (Random)", True, YELLOW)
    medium = FONT.render("2. Medium (Depth 3)", True, YELLOW)
    hard = FONT.render("3. Hard (Depth 5)", True, YELLOW)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    screen.blit(easy, (WIDTH // 2 - easy.get_width() // 2, 200))
    screen.blit(medium, (WIDTH // 2 - medium.get_width() // 2, 300))
    screen.blit(hard, (WIDTH // 2 - hard.get_width() // 2, 400))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1
                if event.key == pygame.K_2:
                    return 3
                if event.key == pygame.K_3:
                    return 5


# ----------------------------------------
# Game Loop
# ----------------------------------------
def gui_game():
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Connect Four (Human vs AI)")

    # Get difficulty
    depth = difficulty_menu(screen)

    # Set up board
    game_board = board.create_board()
    turn = 0  # 0 = human, 1 = AI
    game_over = False

    draw_board(game_board, screen)
    pygame.display.update()

    while not game_over:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Human move (mouse motion shows preview)
            if turn == 0:
                if event.type == pygame.MOUSEMOTION:
                    screen.fill(BLACK, (0, 0, WIDTH, SQUARESIZE))
                    x_pos = event.pos[0]
                    pygame.draw.circle(screen, YELLOW,
                                       (x_pos, SQUARESIZE // 2), RADIUS)
                    pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    col = event.pos[0] // SQUARESIZE
                    valid_moves = board.get_valid_moves(game_board)

                    if col in valid_moves:
                        board.make_move(game_board, col, 1)

                        if board.check_win(game_board, 1):
                            draw_board(game_board, screen)
                            label = FONT.render("You Win!", True, YELLOW)
                            screen.blit(label, (20, 10))
                            pygame.display.update()
                            pygame.time.wait(3000)
                            game_over = True

                        elif board.check_draw(game_board):
                            draw_board(game_board, screen)
                            label = FONT.render("Draw!", True, WHITE)
                            screen.blit(label, (20, 10))
                            pygame.display.update()
                            pygame.time.wait(3000)
                            game_over = True

                        turn = 1  # Switch to AI
                        draw_board(game_board, screen)

            # AI turn
            if turn == 1 and not game_over:
                pygame.time.wait(500)

                col = pick_best_move(game_board, 2, depth=depth)
                board.make_move(game_board, col, 2)

                if board.check_win(game_board, 2):
                    draw_board(game_board, screen)
                    label = FONT.render("AI Wins!", True, RED)
                    screen.blit(label, (20, 10))
                    pygame.display.update()
                    pygame.time.wait(3000)
                    game_over = True

                elif board.check_draw(game_board):
                    draw_board(game_board, screen)
                    label = FONT.render("Draw!", True, WHITE)
                    screen.blit(label, (20, 10))
                    pygame.display.update()
                    pygame.time.wait(3000)
                    game_over = True

                turn = 0
                draw_board(game_board, screen)

    pygame.quit()


if __name__ == "__main__":
    gui_game()
