import pygame
import numpy as np
import itertools
import sys
import networkx as nx
import collections
from utils import make_grid, colrow_to_xy, xy_to_colrow, is_valid_move, get_stone_groups, has_no_liberties, BOARD_WIDTH, BOARD_BROWN, BOARD_BORDER, BLACK, DOT_RADIUS, STONE_RADIUS, WHITE, SCORE_POS, TURN_POS, has_valid_moves
from pygame import gfxdraw
from mcts_ai import MCTSAI

class Game:
    def __init__(self, size):
        self.board = np.zeros((size, size))
        self.size = size
        self.black_turn = True
        self.prisoners = collections.defaultdict(int)
        self.start_points, self.end_points = make_grid(self.size)
        self.prev_pass = False
        self.pass_move = False
        self.pass_move_flag = False  # Track the current pass move
        self.pass_turn = None
        self.consecutive_passes = 0
        self.mcts_ai = MCTSAI(size)

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Go Game")
        screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
        self.screen = screen
        self.ZOINK = pygame.mixer.Sound("wav/zoink.wav")
        self.CLICK = pygame.mixer.Sound("wav/click.wav")
        self.font = pygame.font.SysFont("arial", 30)

    def clear_screen(self):

        # fill board and add gridlines
        self.screen.fill(BOARD_BROWN)
        for start_point, end_point in zip(self.start_points, self.end_points):
            pygame.draw.line(self.screen, BLACK, start_point, end_point)

        # add guide dots
        guide_dots = [3, self.size // 2, self.size - 4]
        for col, row in itertools.product(guide_dots, guide_dots):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, DOT_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, DOT_RADIUS, BLACK)

        pygame.display.flip()

    def make_pass_move(self):
        self.pass_turn = "white" if self.pass_turn == "black" else "black"
        self.black_turn = not self.black_turn
        self.consecutive_passes += 1

        if self.consecutive_passes == 2:
            black_score, white_score = self.calculate_score()

            print(f"Game Over!\nBlack's Score: {black_score}\nWhite's Score: {white_score}")

            # Decide the winner based on the scores
            if black_score > white_score:
                print("Black wins!")
            elif white_score > black_score:
                print("White wins!")
            else:
                print("It's a tie!")

            sys.exit()

        self.draw()


    def has_valid_moves(self):
        return has_valid_moves(self.board, self.size)

    def handle_click(self):
        # get board position
        x, y = pygame.mouse.get_pos()
        col, row = xy_to_colrow(x, y, self.size)
        if not is_valid_move(col, row, self.board):
            self.ZOINK.play()
            return
        self.consecutive_passes = 0

        # update board array
        self.board[col, row] = 1 if self.black_turn else 2

        # get stone groups for black and white
        self_color = "black" if self.black_turn else "white"
        other_color = "white" if self.black_turn else "black"

        # handle captures
        capture_happened = False
        for group in list(get_stone_groups(self.board, other_color)):
            if has_no_liberties(self.board, group):
                capture_happened = True
                for i, j in group:
                    self.board[i, j] = 0
                self.prisoners[self_color] += len(group)

        # handle special case of invalid stone placement
        # this must be done separately because we need to know if capture resulted
        if not capture_happened:
            group = None
            for group in get_stone_groups(self.board, self_color):
                if (col, row) in group:
                    break
            if has_no_liberties(self.board, group):
                self.ZOINK.play()
                self.board[col, row] = 0
                return
            
        self.pass_move_flag = False
        # change turns and draw screen
        self.CLICK.play()
        self.black_turn = not self.black_turn
        self.consecutive_passes = 0  # Reset consecutive passes
        self.pass_turn = None  # Reset pass turn
        self.draw()

    def is_game_over(self):
        if self.prev_pass and self.pass_move:  # Check for consecutive passes
            return True

        # Check for no valid moves left
        for col in range(self.size):
            for row in range(self.size):
                if is_valid_move(col, row, self.board):
                    return False  # There is a valid move, the game is not over

        # Check for prisoners
        if self.prisoners['black'] + self.prisoners['white'] >= 10:
            return True  # Arbitrary condition for the example, adjust as needed

        # Add more conditions as needed

        return False  # If none of the above conditions are met, the game is not over

    def draw(self):
        # draw stones - filled circle and antialiased ring
        self.clear_screen()
        for col, row in zip(*np.where(self.board == 1)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, BLACK)
        for col, row in zip(*np.where(self.board == 2)):
            x, y = colrow_to_xy(col, row, self.size)
            gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, WHITE)
            gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, WHITE)

        # text for score and turn info
        score_msg = (
        f"Black's Prisoners: {self.prisoners['black']}"
        + f"     White's Prisoners: {self.prisoners['white']}"
        )
        txt = self.font.render(score_msg, True, BLACK)
        self.screen.blit(txt, SCORE_POS)
        turn_msg = (
            f"{'Black' if self.black_turn else 'White'} to move. "
            + "Click to place stone, press P to pass."
        )
        txt = self.font.render(turn_msg, True, BLACK)
        self.screen.blit(txt, TURN_POS)

        pygame.display.flip()

    def calculate_score(self):
        black_territory = 0
        white_territory = 0

        # Count territory by iterating through the board
        for col in range(self.size):
            for row in range(self.size):
                if self.board[col, row] == 0:
                    neighbors = [(col - 1, row), (col + 1, row), (col, row - 1), (col, row + 1)]
                    neighboring_colors = [self.board[x, y] for x, y in neighbors if 0 <= x < self.size and 0 <= y < self.size]

                    if 1 in neighboring_colors and 2 not in neighboring_colors:
                        black_territory += 1
                    elif 2 in neighboring_colors and 1 not in neighboring_colors:
                        white_territory += 1

        # Add prisoners to the score
        black_score = black_territory + self.prisoners["black"]
        white_score = white_territory + self.prisoners["white"]

        return black_score, white_score

    def update(self):
        # TODO: undo button
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                self.handle_click()
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    self.make_pass_move()

        # Add the additional condition for the AI's move
        if not self.black_turn:
            ai_move = self.mcts_ai.get_move(self.board)
            if ai_move:
                col, row = ai_move
                self.board[col, row] = 2  # Assuming 2 represents white stones
                self.black_turn = not self.black_turn
                self.consecutive_passes = 0
                self.pass_turn = None
                self.draw()    

    def end_game(self):
    # Add logic to determine the winner or declare a tie
        print("Game Over!")
        sys.exit()