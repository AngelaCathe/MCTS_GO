import numpy as np

class MCTSAI:
    def __init__(self, size):
        # Initialize any necessary variables or parameters for the AI
        self.size = size

    def select_node(self, node):
        while node.children:
            node = max(node.children, key=lambda child: self.ucb_score(child))
        return node

    def expand_node(self, node):
        legal_moves = self.get_legal_moves(node.board)

        if not legal_moves:
            return None

        child_nodes = []
        for move in legal_moves:
            new_board = node.board.copy()
            new_board[move] = 2  # Assume white stones for the AI
            child_node = Node(new_board)
            child_node.parent = node
            child_node.move = move
            child_nodes.append(child_node)

        # Select the child with the highest UCB score
        selected_child = max(child_nodes, key=lambda child: self.ucb_score(child))

        return selected_child
        # return node.children[0]  # Return the first child for simplicity; you can enhance this

    def get_legal_moves(self, board):
        # Implement a function to get the legal moves based on the current board state
        # Return a list of (col, row) tuples representing legal moves
        legal_moves = []

        for col in range(self.size):
            for row in range(self.size):
                if self.is_valid_move(col, row, board):
                    legal_moves.append((col, row))

        return legal_moves

    def is_valid_move(self, col, row, board):
        if col < 0 or col >= board.shape[0]:
            return False
        if row < 0 or row >= board.shape[0]:
            return False
        return board[col, row] == 0  


    def get_move(self, board):
        # Implement the MCTS algorithm to get the AI's move based on the current game state
        # Return the chosen move as (col, row)

        root = Node(board.copy())  # Create a root node with the current board state

        # Add your MCTS algorithm here

        # Run MCTS for a certain number of iterations (adjust as needed)
        for _ in range(1):
            selected_node = self.select_node(root)
            expanded_node = self.expand_node(selected_node)
            simulation_result = self.simulate(expanded_node)
            self.backpropagate(expanded_node, simulation_result)

        # Select the best move based on the MCTS results
        best_move = self.select_best_move(root)

        return best_move

    def select_best_move(self, root):
        if root.children:
            best_child = max(root.children, key=lambda child: self.ucb_score(child))
            return best_child.move
        else:
            return None
        
    def ucb_score(self, node):
        if node.visits == 0:
            return float('inf') # Treat unvisited nodes as infinitely valuable

        exploration_weight = 1.0 / np.sqrt(2.0)
        exploitation_score = node.wins / node.visits
        exploration_score = exploration_weight * np.sqrt(np.log(node.parent.visits) / node.visits)
        ucb_score = exploitation_score + exploration_score
        return ucb_score

    def simulate(self,node):
        while not self.is_terminal(node):
            legal_moves = self.get_legal_moves(node.board)

            if not legal_moves:
                break #no legal moves, end the simulation

            random_move = np.random.choice(np.ravel(legal_moves)) # Flatten the legal_moves array
            col, row = divmod(random_move, self.size)
            node.board[col, row] = 2 if node.is_max else 1


            node.is_max = not node.is_max  # Switch player turn

        result = self.get_result(node.board)
        return result
    
    def is_terminal(self, node):
        return not self.has_valid_moves(node.board)

    def has_valid_moves(self, board):
        return any(self.is_valid_move(col, row, board) for col in range(self.size) for row in range(self.size))

    def get_result(self, board):
        black_prisoners = np.sum(board == 1)  # Assuming black stones are represented by 1
        white_prisoners = np.sum(board == 2)  # Assuming white stones are represented by 2

        if black_prisoners > white_prisoners:
            return 1  # Black wins
        elif black_prisoners < white_prisoners:
            return -1  # White wins
        else:
            return 0  # It's a draw

class Node:
    def __init__(self, board):
        self.board = board
        self.children = []
        self.visits = 0
        self.wins = 0
        self.parent = None
        self.move = None
        self.is_max = True
        self.expanded = False

