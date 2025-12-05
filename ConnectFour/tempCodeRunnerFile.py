# gui.py
# Connect Four GUI using Tkinter with AI opponent

import tkinter as tk
from tkinter import messagebox
import board
from ai import pick_best_move, random_move

ROWS, COLS = 6, 7
CELL_SIZE = 80
PLAYER_PIECE = 1
AI_PIECE = 2

class ConnectFourGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Connect Four")
        self.canvas = tk.Canvas(master, width=COLS*CELL_SIZE, height=(ROWS+1)*CELL_SIZE, bg="blue")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.human_move)

        # Difficulty selection
        self.difficulty_var = tk.IntVar(value=2)
        tk.Label(master, text="Difficulty:").pack()
        tk.Radiobutton(master, text="Easy (Random)", variable=self.difficulty_var, value=1).pack()
        tk.Radiobutton(master, text="Medium (Depth 2)", variable=self.difficulty_var, value=2).pack()
        tk.Radiobutton(master, text="Hard (Depth 4)", variable=self.difficulty_var, value=3).pack()

        tk.Button(master, text="New Game", command=self.new_game).pack()
        self.new_game()

    def new_game(self):
        self.game_board = board.create_board()
        self.game_over = False
        self.turn = 0  # 0 = human, 1 = AI
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x0 = c * CELL_SIZE
                y0 = (r+1) * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                cell = self.game_board[r][c]
                if cell == 0:
                    color = "white"
                elif cell == PLAYER_PIECE:
                    color = "red"
                else:
                    color = "yellow"
                self.canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill=color)

    def human_move(self, event):
        if self.game_over or self.turn != 0:
            return
        col = event.x // CELL_SIZE
        if col not in board.get_valid_moves(self.game_board):
            return
        board.make_move(self.game_board, col, PLAYER_PIECE)
        if board.check_win(self.game_board, PLAYER_PIECE):
            self.draw_board()
            messagebox.showinfo("Game Over", "Congratulations! You win!")
            self.game_over = True
            return
        elif board.check_draw(self.game_board):
            self.draw_board()
            messagebox.showinfo("Game Over", "It's a draw!")
            self.game_over = True
            return

        self.turn = 1
        self.draw_board()
        self.master.after(200, self.ai_move)

    def ai_move(self):
        if self.game_over or self.turn != 1:
            return
        difficulty = self.difficulty_var.get()
        if difficulty == 1:
            col = random_move(self.game_board)
        elif difficulty == 2:
            col, _, _ = pick_best_move(self.game_board, AI_PIECE, depth=2)
        else:
            col, _, _ = pick_best_move(self.game_board, AI_PIECE, depth=4)

        board.make_move(self.game_board, col, AI_PIECE)

        if board.check_win(self.game_board, AI_PIECE):
            self.draw_board()
            messagebox.showinfo("Game Over", "AI wins! Better luck next time.")
            self.game_over = True
            return
        elif board.check_draw(self.game_board):
            self.draw_board()
            messagebox.showinfo("Game Over", "It's a draw!")
            self.game_over = True
            return

        self.turn = 0
        self.draw_board()


if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourGUI(root)
    root.mainloop()
