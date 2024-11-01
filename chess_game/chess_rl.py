import pygame
import numpy as np
import random

# Initialize Pygame
pygame.init()

# Set display dimensions
WIDTH, HEIGHT = 640, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set title
pygame.display.set_caption("Chess Game")

# Define board dimensions
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define board
board = [
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
]

# Q-learning parameters
alpha = 0.1    # Learning rate
gamma = 0.9    # Discount factor
epsilon = 0.1  # Exploration rate
q_table = {}

# Define function to draw board
def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = BLACK if (row + col) % 2 == 0 else WHITE
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board[row][col]
            if piece != '.':
                font = pygame.font.SysFont(None, 50)
                piece_text = font.render(piece, True, BLACK if piece.islower() else WHITE)
                screen.blit(piece_text, (col * SQUARE_SIZE + 10, row * SQUARE_SIZE + 10))

# Define function to update display
def update_display():
    draw_board()
    pygame.display.update()

# Define function to move piece
def move_piece(row1, col1, row2, col2):
    piece = board[row1][col1]
    board[row1][col1] = '.'
    board[row2][col2] = piece

# Define function to check if move is valid
# Define function to check if move is valid
def is_valid_move(row1, col1, row2, col2):
    piece = board[row1][col1]
    target_piece = board[row2][col2]
    
    # Ensure that the starting square has a piece and the target is either empty or an opponent's piece
    if piece == '.' or (target_piece != '.' and (piece.isupper() == target_piece.isupper())):
        print("Invalid: No piece at start or same color at target.")
        return False

    delta_row = row2 - row1
    delta_col = col2 - col1

    # Pawn movement
    if piece.upper() == 'P':
        direction = -1 if piece.isupper() else 1  # White moves up (-1), Black moves down (+1)
        start_row = 6 if piece.isupper() else 1

        # Single move forward
        if col1 == col2 and delta_row == direction and board[row2][col2] == '.':
            return True
        # Initial two-square move
        if col1 == col2 and row1 == start_row and delta_row == 2 * direction:
            if board[row1 + direction][col1] == '.' and board[row2][col2] == '.':
                return True
        # Diagonal capture
        if abs(delta_col) == 1 and delta_row == direction and target_piece != '.' and piece.isupper() != target_piece.isupper():
            return True
        return False  # No pawn move condition met

    # Rook movement
    if piece.upper() == 'R':
        # Rooks can only move along rows or columns (either delta_row or delta_col must be zero)
        if delta_row == 0 or delta_col == 0:
            if not is_path_blocked(row1, col1, row2, col2):
                print("Valid: Rook move.")
                return True
            else:
                print("Invalid: Path blocked for Rook.")
        else:
            print("Invalid: Rook must move in a straight line.")
        return False  # Invalid Rook move condition

    # Knight movement
    elif piece.upper() == 'N':
        return (abs(delta_row), abs(delta_col)) in [(2, 1), (1, 2)]
    
    # Bishop movement
    elif piece.upper() == 'B':
        if abs(delta_row) == abs(delta_col):
            return not is_path_blocked(row1, col1, row2, col2)
    
    # Queen movement
    elif piece.upper() == 'Q':
        if delta_row == 0 or delta_col == 0 or abs(delta_row) == abs(delta_col):
            return not is_path_blocked(row1, col1, row2, col2)
    
    # King movement
    elif piece.upper() == 'K':
        return max(abs(delta_row), abs(delta_col)) == 1

    return False

# Check if path is blocked for Rook, Bishop, and Queen
def is_path_blocked(row1, col1, row2, col2):
    step_row = (row2 - row1) // max(1, abs(row2 - row1)) if row1 != row2 else 0
    step_col = (col2 - col1) // max(1, abs(col2 - col1)) if col1 != col2 else 0
    
    row, col = row1 + step_row, col1 + step_col
    while (row, col) != (row2, col2):
        if board[row][col] != '.':
            return True
        row += step_row
        col += step_col
    return False


# Q-learning AI Move Logic
def get_state_representation():
    return tuple(np.array(board).flatten())

def choose_action(state):
    if random.random() < epsilon:  # Exploration
        return random.choice(get_all_possible_moves('black'))
    return max(q_table.get(state, {}).items(), key=lambda x: x[1])[0] if state in q_table else None

def get_all_possible_moves(color):
    moves = []
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if (piece.isupper() and color == 'white') or (piece.islower() and color == 'black'):
                moves.extend(get_piece_moves(row, col))
    return moves

def update_q_table(state, action, reward, next_state):
    max_future_q = max(q_table.get(next_state, {}).values(), default=0)
    current_q = q_table.get(state, {}).get(action, 0)
    q_table[state][action] = current_q + alpha * (reward + gamma * max_future_q - current_q)

def get_piece_moves(row, col):
    moves = []
    piece = board[row][col]
    for r in range(ROWS):
        for c in range(COLS):
            if is_valid_move(row, col, r, c):
                moves.append((row, col, r, c))
    return moves

# Initialize variables
selected_piece = None
selected_position = None
player_turn = 'white'

# Define function to handle clicks and turns
def handle_click(row, col):
    global selected_piece, selected_position, player_turn

    piece = board[row][col]
    
    if selected_piece is None:
        if (piece.isupper() and player_turn == 'white') or (piece.islower() and player_turn == 'black'):
            selected_piece = piece
            selected_position = (row, col)
            print(f"Selected piece: {piece} at ({row}, {col})")
    else:
        start_row, start_col = selected_position
        if is_valid_move(start_row, start_col, row, col):
            print(f"Moving piece {selected_piece} from ({start_row}, {start_col}) to ({row}, {col})")
            move_piece(start_row, start_col, row, col)
            player_turn = 'black' if player_turn == 'white' else 'white'  # Switch turn
        else:
            print("Invalid move")
        
        selected_piece = None
        selected_position = None

# Game loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and player_turn == 'white':
            row, col = event.pos[1] // SQUARE_SIZE, event.pos[0] // SQUARE_SIZE
            handle_click(row, col)
    
    # AI's turn
    if player_turn == 'black':
        state = get_state_representation()
        action = choose_action(state)
        if action:
            row1, col1, row2, col2 = action
            move_piece(row1, col1, row2, col2)
            player_turn = 'white'

    update_display()
    clock.tick(60)
