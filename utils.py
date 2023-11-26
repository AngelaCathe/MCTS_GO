import numpy as np
import itertools
import networkx as nx
from pygame import gfxdraw

BOARD_BROWN = (199, 105, 42)
BOARD_WIDTH = 750
BOARD_BORDER = 50
STONE_RADIUS = 22
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TURN_POS = (BOARD_BORDER, 10)
SCORE_POS = (BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER + 10)
DOT_RADIUS = 4

def make_grid(size):
    """Return list of (start_point, end_point pairs) defining gridlines

    Args:
        size (int): size of grid

    Returns:
        Tuple[List[Tuple[float, float]]]: start and end points for gridlines
    """
    start_points, end_points = [], []

    # vertical start points (constant y)
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_BORDER)
    start_points += list(zip(xs, ys))

    # horizontal start points (constant x)
    xs = np.full((size), BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    start_points += list(zip(xs, ys))

    # vertical end points (constant y)
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    end_points += list(zip(xs, ys))

    # horizontal end points (constant x)
    xs = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    end_points += list(zip(xs, ys))

    return (start_points, end_points)


def xy_to_colrow(x, y, size):
    """Convert x,y coordinates to column and row number

    Args:
        x (float): x position
        y (float): y position
        size (int): size of grid

    Returns:
        Tuple[int, int]: column and row numbers of intersection
    """
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x_dist = x - BOARD_BORDER
    y_dist = y - BOARD_BORDER
    col = int(round(x_dist / inc))
    row = int(round(y_dist / inc))
    return col, row


def colrow_to_xy(col, row, size):
    """Convert column and row numbers to x,y coordinates

    Args:
        col (int): column number (horizontal position)
        row (int): row number (vertical position)
        size (int): size of grid

    Returns:
        Tuple[float, float]: x,y coordinates of intersection
    """
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x = int(BOARD_BORDER + col * inc)
    y = int(BOARD_BORDER + row * inc)
    return x, y


def has_no_liberties(board, group):
    """Check if a stone group has any liberties on a given board.

    Args:
        board (object): game board (size * size matrix)
        group (List[Tuple[int, int]]): list of (col,row) pairs defining a stone group

    Returns:
        [boolean]: True if group has any liberties, False otherwise
    """
    for x, y in group:
        if x > 0 and board[x - 1, y] == 0:
            return False
        if y > 0 and board[x, y - 1] == 0:
            return False
        if x < board.shape[0] - 1 and board[x + 1, y] == 0:
            return False
        if y < board.shape[0] - 1 and board[x, y + 1] == 0:
            return False
    return True


def get_stone_groups(board, color):
    """Get stone groups of a given color on a given board

    Args:
        board (object): game board (size * size matrix)
        color (str): name of color to get groups for

    Returns:
        List[List[Tuple[int, int]]]: list of list of (col, row) pairs, each defining a group
    """
    size = board.shape[0]
    color_code = 1 if color == "black" else 2
    xs, ys = np.where(board == color_code)
    graph = nx.grid_graph(dim=[size, size])
    stones = set(zip(xs, ys))
    all_spaces = set(itertools.product(range(size), range(size)))
    stones_to_remove = all_spaces - stones
    graph.remove_nodes_from(stones_to_remove)
    return nx.connected_components(graph)


def is_valid_move(col, row, board):
    # TODO: check for ko situation (infinite back and forth)
    if col < 0 or col >= board.shape[0]:
        return False
    if row < 0 or row >= board.shape[0]:
        return False
    return board[col, row] == 0

def has_valid_moves(board, size):
    for col in range(size):
        for row in range(size):
            if is_valid_move(col, row, board):
                return True
    return False

    """Check if placing a stone at (col, row) is valid on board

    Args:
        col (int): column number
        row (int): row number
        board (object): board grid (size * size matrix)

    Returns:
        boolean: True if move is valid, False otherewise
    """