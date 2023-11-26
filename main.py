import pygame
import sys
from game import Game
from utils import make_grid

if __name__ == "__main__":
    g = Game(size=9)
    g.init_pygame()
    g.clear_screen()
    g.draw()

    while True:
        g.update()

        # Check for the game over state
        if g.is_game_over():
            print("Game Over!")
            # Perform any actions needed for the end of the game
            # (e.g., display a winner, perform scoring, etc.)
            pygame.time.wait(2000)  # Wait for 2 seconds before exiting
            pygame.quit()
            sys.exit()

        pygame.time.wait(100)