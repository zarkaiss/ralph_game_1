import sys
import math
import random
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
ANIMATION_SPEED = 0.18

# Design Palette
COLOR_BG = (20, 20, 30)
COLOR_GRID_LINE = (40, 40, 60)
COLOR_TEXT = (230, 230, 250)
COLOR_SELECT = (255, 215, 0)
COLOR_OVERLAY = (0, 0, 0, 180) # Semi-transparent black for menus

GEM_COLORS = {
    1: (240, 90, 120),
    2: (255, 150, 50),
    3: (250, 220, 80),
    4: (80, 210, 120),
    5: (70, 160, 245)
}

class Particle:
    """Handles physics and rendering for shattered gem fragments."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # Explode outwards in random directions
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 255  # Alpha channel/lifetime
        self.size = random.uniform(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # Gravity
        self.life -= 8  # Fade out speed

    def draw(self, surface):
        if self.life > 0:
            # Create a temporary surface for alpha blending
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            alpha_color = (*self.color, max(0, min(255, self.life)))
            pygame.draw.circle(surf, alpha_color, (int(self.size), int(self.size)), int(self.size))
            surface.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class VisualGem:
    """Manages the visual lifecycle, positions, and animations of individual gems."""
    def __init__(self, gem_id, start_row, start_col, spawn_above=False):
        self.gem_id = gem_id
        self.row = start_row
        self.col = start_col
        
        self.target_x = self.col * TILE_SIZE + TILE_SIZE // 2
        self.target_y = (self.row * TILE_SIZE) + UI_PANEL_HEIGHT + TILE_SIZE // 2
        
        self.x = self.target_x
        if spawn_above:
            self.y = (start_row - ROWS) * TILE_SIZE + UI_PANEL_HEIGHT - TILE_SIZE // 2
        else:
            self.y = self.target_y

    def update_target(self, new_row, new_col):
        self.row = new_row
        self.col = new_col
        self.target_x = self.col * TILE_SIZE + TILE_SIZE // 2
        self.target_y = (self.row * TILE_SIZE) + UI_PANEL_HEIGHT + TILE_SIZE // 2

    def step_animation(self):
        self.x += (self.target_x - self.x) * ANIMATION_SPEED
        self.y += (self.target_y - self.y) * ANIMATION_SPEED

    def draw(self, surface):
        color = GEM_COLORS.get(self.gem_id, (200, 200, 200))
        size = int(TILE_SIZE * 0.32)
        cx, cy = int(self.x), int(self.y)

        if self.gem_id == 1:
            pygame.draw.circle(surface, color, (cx, cy), size)
            pygame.draw.circle(surface, (255, 255, 255), (cx - size//3, cy - size//3), size//4)
        elif self.gem_id == 2:
            points = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
            pygame.draw.polygon(surface, color, points)
        elif self.gem_id == 3:
            points = [(cx, cy - size), (cx + size, cy + size), (cx - size, cy + size)]
            pygame.draw.polygon(surface, color, points)
        elif self.gem_id == 4:
            rect = pygame.Rect(cx - size, cy - size, size * 2, size * 2)
            pygame.draw.rect(surface, color, rect, border_radius=8)
        elif self.gem_id == 5:
            arm = size // 3
            points = [
                (cx - arm, cy - size), (cx + arm, cy - size), (cx + arm, cy - arm),
                (cx + size, cy - arm), (cx + size, cy + arm), (cx + arm, cy + arm),
                (cx + arm, cy + size), (cx - arm, cy + size), (cx - arm, cy + arm),
                (cx - size, cy + arm), (cx - size, cy - arm), (cx - arm, cy - arm)
            ]
            pygame.draw.polygon(surface, color, points)

def sync_visual_board(engine, current_visuals):
    """
    Compares the current memory engine state array against active visual instances.
    Returns the new visual grid AND a list of destroyed gems for particle generation.
    """
    board = engine.get_board()
    next_visuals = [[None for _ in range(COLS)] for _ in range(ROWS)]
    
    pool = []
    for r in range(ROWS):
        for c in range(COLS):
            if current_visuals[r][c] is not None:
                pool.append(current_visuals[r][c])

    for c in range(COLS):
        for r in range(ROWS - 1, -1, -1):
            target_id = board[r][c]
            match_found = None
            for vg in pool:
                if vg.gem_id == target_id and vg.col == c:
                    match_found = vg
                    pool.remove(vg)
                    break
            
            if match_found:
                match_found.update_target(r, c)
                next_visuals[r][c] = match_found
            else:
                next_visuals[r][c] = VisualGem(target_id, r, c, spawn_above=True)
                
    # Any gems left in the pool were destroyed in a match
    return next_visuals, pool

def main():
    pygame.init()
    pygame.font.init()
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Match-3: Particle & Level Edition")
    clock = pygame.time.Clock()
    
    font_sm = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_lg = pygame.font.SysFont("Segoe UI", 36, bold=True)
    
    engine = MatchThreeEngine(rows=ROWS, cols=COLS)
    state = GameState(engine)
    
    visual_grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    board = engine.get_board()
    for r in range(ROWS):
        for c in range(COLS):
            visual_grid[r][c] = VisualGem(board[r][c], r, c, spawn_above=False)
            
    selected_tile = None
    active_particles = []
    
    # --- Level Progression Variables ---
    LEVEL_DURATION = 60.0
    current_level = 1
    level_timer = LEVEL_DURATION
    
    level_start_score = 0
    # Level 1 requires you to score 500 points to pass
    target_score = 500 
    
    game_mode = "PLAYING" # States: PLAYING, LEVEL_UP, GAME_OVER
    transition_timer = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # --- Progression Logic ---
        if game_mode == "PLAYING":
            level_timer -= dt
            if level_timer <= 0:
                if engine.get_score() >= target_score:
                    # Level Up Success
                    game_mode = "LEVEL_UP"
                    transition_timer = 3.0
                    
                    # Calculate next level requirements
                    last_gain = engine.get_score() - level_start_score
                    current_level += 1
                    level_start_score = engine.get_score()
                    
                    # Next target is your new score + what you gained last level + a difficulty bump
                    target_score = level_start_score + last_gain + 250
                else:
                    # Failed to hit target
                    game_mode = "GAME_OVER"
                    
        elif game_mode == "LEVEL_UP":
            transition_timer -= dt
            if transition_timer <= 0:
                level_timer = LEVEL_DURATION
                game_mode = "PLAYING"

        # --- Input Pipeline ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_mode != "PLAYING":
                    continue # Lock inputs during transitions
                
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if mouse_y >= UI_PANEL_HEIGHT:
                    col = mouse_x // TILE_SIZE
                    row = (mouse_y - UI_PANEL_HEIGHT) // TILE_SIZE
                    
                    if selected_tile is None:
                        selected_tile = (row, col)
                    elif selected_tile == (row, col):
                        selected_tile = None
                    else:
                        r1, c1 = selected_tile
                        r2, c2 = row, col
                        
                        if abs(r1 - r2) + abs(c1 - c2) == 1:
                            success = engine.swap(r1, c1, r2, c2)
                            if success:
                                engine.process_cascade()
                                state.record_valid_move()
                                
                                # Sync visuals and catch destroyed gems for particles
                                visual_grid, destroyed_gems = sync_visual_board(engine, visual_grid)
                                
                                # Spawn particles for every destroyed gem
                                for d_gem in destroyed_gems:
                                    color = GEM_COLORS.get(d_gem.gem_id, (255, 255, 255))
                                    for _ in range(12): # 12 particles per gem
                                        active_particles.append(Particle(d_gem.x, d_gem.y, color))
                                        
                            else:
                                state.record_invalid_move()
                            selected_tile = None
                        else:
                            selected_tile = (row, col)
                            
        state.check_exit_conditions()
        if state.game_over and game_mode == "PLAYING":
            game_mode = "GAME_OVER"

        # --- Update Step ---
        for r in range(ROWS):
            for c in range(COLS):
                if visual_grid[r][c]:
                    visual_grid[r][c].step_animation()
                    
        for p in active_particles[:]:
            p.update()
            if p.life <= 0:
                active_particles.remove(p)

        # --- Draw Step ---
        screen.fill(COLOR_BG)
        
        # Draw UI Panel
        top_y = 15
        bot_y = 50
        
        # Top Row UI
        level_lbl = font_sm.render(f"LEVEL {current_level}", True, COLOR_TEXT)
        time_lbl = font_sm.render(f"TIME: {max(0, int(level_timer))}s", True, COLOR_TEXT)
        screen.blit(level_lbl, (20, top_y))
        screen.blit(time_lbl, (WINDOW_WIDTH - time_lbl.get_width() - 20, top_y))
        
        # Bottom Row UI
        score_lbl = font_sm.render(f"SCORE: {engine.get_score()}", True, COLOR_TEXT)
        target_lbl = font_sm.render(f"TARGET: {target_score}", True, COLOR_SELECT)
        screen.blit(score_lbl, (20, bot_y))
        screen.blit(target_lbl, (WINDOW_WIDTH - target_lbl.get_width() - 20, bot_y))
        
        # Draw static underlying layout
        for r in range(ROWS):
            for c in range(COLS):
                tile_rect = pygame.Rect(c * TILE_SIZE, (r * TILE_SIZE) + UI_PANEL_HEIGHT, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, COLOR_GRID_LINE, tile_rect, 1)
                
        # Draw moving items
        for r in range(ROWS):
            for c in range(COLS):
                if visual_grid[r][c]:
                    visual_grid[r][c].draw(screen)
                    
        # Draw Particles on top of gems
        for p in active_particles:
            p.draw(screen)
                    
        # Overlay selection highlight
        if selected_tile:
            sr, sc = selected_tile
            select_rect = pygame.Rect(sc * TILE_SIZE, (sr * TILE_SIZE) + UI_PANEL_HEIGHT, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLOR_SELECT, select_rect, 3, border_radius=4)
            
        # Draw Overlay Menus
        if game_mode == "LEVEL_UP":
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_OVERLAY)
            screen.blit(overlay, (0, 0))
            
            msg = font_lg.render("LEVEL CLEARED!", True, COLOR_SELECT)
            screen.blit(msg, (WINDOW_WIDTH//2 - msg.get_width()//2, WINDOW_HEIGHT//2 - 40))
            
        elif game_mode == "GAME_OVER":
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill(COLOR_OVERLAY)
            screen.blit(overlay, (0, 0))
            
            msg = font_lg.render("GAME OVER", True, (240, 90, 120))
            sub_msg = font_sm.render(f"Final Score: {engine.get_score()}", True, COLOR_TEXT)
            screen.blit(msg, (WINDOW_WIDTH//2 - msg.get_width()//2, WINDOW_HEIGHT//2 - 40))
            screen.blit(sub_msg, (WINDOW_WIDTH//2 - sub_msg.get_width()//2, WINDOW_HEIGHT//2 + 10))
            
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()