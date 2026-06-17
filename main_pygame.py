import sys
import pygame
from src.game_logic import MatchThreeEngine
from src.game_state import GameState

# Configuration Constants
ROWS = 8
COLS = 8
TILE_SIZE = 75
UI_PANEL_HEIGHT = 100

WINDOW_WIDTH = COLS * TILE_SIZE
WINDOW_HEIGHT = (ROWS * TILE_SIZE) + UI_PANEL_HEIGHT
FPS = 60

# Color Palette
COLOR_BG = (24, 24, 37)          # Dark Slate
COLOR_GRID_LINE = (49, 50, 68)   # Subtle Muted Divider
COLOR_TEXT = (205, 214, 244)     # Off-white
COLOR_SELECT = (245, 224, 220)   # Light Highlight Accent

# Gem Visual Mapping (IDs 1-5 mapped to RGB values)
GEM_COLORS = {
    1: (243, 139, 168),  # Soft Red
    2: (250, 179, 135),  # Soft Orange
    3: (249, 226, 175),  # Soft Yellow
    4: (166, 227, 161),  # Soft Green
    5: (137, 180, 250)   # Soft Blue
}

def main():
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Match-3 Puzzle Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24, bold=True)
    
    # Initialize your pristine, fully tested core backend engine
    engine = MatchThreeEngine(rows=ROWS, cols=COLS)
    state = GameState(engine)
    
    selected_tile = None  # Tracks the first clicked tile coordinate tuple: (row, col)
    
    running = True
    while running:
        # 1. Input / Event Handling Pipeline
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Check if the click happened inside the playable grid area
                if mouse_y >= UI_PANEL_HEIGHT:
                    col = mouse_x // TILE_SIZE
                    row = (mouse_y - UI_PANEL_HEIGHT) // TILE_SIZE
                    
                    # Selection State Logic Engine
                    if selected_tile is None:
                        selected_tile = (row, col)
                    elif selected_tile == (row, col):
                        selected_tile = None  # Deselect if clicking the same tile twice
                    else:
                        r1, c1 = selected_tile
                        r2, c2 = row, col
                        
                        # Validate adjacency on the frontend for crisp interaction feedback
                        if abs(r1 - r2) + abs(c1 - c2) == 1:
                            success = engine.swap(r1, c1, r2, c2)
                            if success:
                                engine.process_cascade()
                                state.record_valid_move()
                            else:
                                state.record_invalid_move()
                            selected_tile = None  # Clear selection after a move attempt
                        else:
                            # If the second click is far away, shift selection to the new tile
                            selected_tile = (row, col)
                            
        # Check game execution boundaries
        state.check_exit_conditions()
        if state.game_over:
            running = False

        # 2. Graphical Rendering Pipeline
        screen.fill(COLOR_BG)
        
        # Draw UI Information Panel
        score_text = font.render(f"Score: {engine.get_score()}", True, COLOR_TEXT)
        turn_text = font.render(f"Turn: {state.turn_count}", True, COLOR_TEXT)
        screen.blit(score_text, (20, 20))
        screen.blit(turn_text, (WINDOW_WIDTH - 140, 20))
        
        # Render Playable Grid Blocks
        board = engine.get_board()
        for r in range(ROWS):
            for c in range(COLS):
                # Calculate screen destination space
                tile_rect = pygame.Rect(
                    c * TILE_SIZE, 
                    (r * TILE_SIZE) + UI_PANEL_HEIGHT, 
                    TILE_SIZE, 
                    TILE_SIZE
                )
                
                # Render structural grid outlines
                pygame.draw.rect(screen, COLOR_GRID_LINE, tile_rect, 1)
                
                # Draw individual Gem primitives using the ID palette mapping
                gem_id = board[r][c]
                if gem_id in GEM_COLORS:
                    # Inset the geometry slightly for a clean layout border spacing
                    gem_rect = tile_rect.inflate(-16, -16)
                    pygame.draw.rect(screen, GEM_COLORS[gem_id], gem_rect, border_radius=12)
                
                # Highlight the active selected item
                if selected_tile == (r, c):
                    pygame.draw.rect(screen, COLOR_SELECT, tile_rect, 3, border_radius=4)
                    
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()