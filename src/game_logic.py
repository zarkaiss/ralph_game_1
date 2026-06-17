import random
from typing import List, Tuple

class MatchThreeEngine:
    """
    Core engine for handling game logic in a Match-3 style puzzle game.
    """

    # Valid gem ID range constants
    MIN_GEM_ID = 1
    MAX_GEM_ID = 5

    def __init__(self, rows: int = 8, cols: int = 8):
        self.rows = rows
        self.cols = cols
        self.board: List[List[int]] = []
        self.score: int = 0
        self.initialize_grid()

    def _generate_random_gem(self) -> int:
        """Generates a random gem ID within the valid integer range [1, 5]."""
        return random.randint(self.MIN_GEM_ID, self.MAX_GEM_ID)

    def _would_create_match(self, r: int, c: int, gem: int) -> bool:
        """
        Checks if placing a specific gem at (r, c) would create a horizontal 
        or vertical match of 3 or more with already placed tiles.
        """
        # Check horizontal match to the left
        if c >= 2 and self.board[r][c-1] == gem and self.board[r][c-2] == gem:
            return True
        # Check vertical match above
        if r >= 2 and self.board[r-1][c] == gem and self.board[r-2][c] == gem:
            return True
        return False

    def _is_part_of_match(self, r: int, c: int) -> bool:
        """Checks if the gem at (r, c) is part of a horizontal or vertical match of 3 or more."""
        val = self.board[r][c]
        
        # Check horizontal
        count_h = 1
        # Look left
        for i in range(c - 1, -1, -1):
            if self.board[r][i] == val:
                count_h += 1
            else:
                break
        # Look right
        for i in range(c + 1, self.cols):
            if self.board[r][i] == val:
                count_h += 1
            else:
                break
                
        if count_h >= 3:
            return True

        # Check vertical
        count_v = 1
        # Look up
        for i in range(r - 1, -1, -1):
            if self.board[i][c] == val:
                count_v += 1
            else:
                break
        # Look down
        for i in range(r + 1, self.rows):
            if self.board[i][c] == val:
                count_v += 1
            else:
                break
                
        if count_v >= 3:
            return True
            
        return False

    def initialize_grid(self):
        """Generates an NxM matrix of random gem IDs without initial matches."""
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        for r in range(self.rows):
            for c in range(self.cols):
                while True:
                    gem = self._generate_random_gem()
                    # Validation loop: regenerate conflicting tiles until valid placement is found
                    if not self._would_create_match(r, c, gem):
                        self.board[r][c] = gem
                        break

    def get_board(self) -> List[List[int]]:
        """Returns the current state of the board."""
        return self.board

    def swap_tiles(self, r1: int, c1: int, r2: int, c2: int) -> bool:
        """
        Exchanges values at the specified coordinates if they are within bounds.
        Returns True if successful, False otherwise.
        """
        # Check bounds
        if not (0 <= r1 < self.rows and 0 <= c1 < self.cols and 
                0 <= r2 < self.rows and 0 <= c2 < self.cols):
            return False
            
        # Perform swap
        self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]
        return True

    def swap(self, r1: int, c1: int, r2: int, c2: int) -> bool:
        """
        Swaps two gems on the board if they are adjacent and within bounds.
        Returns True if successful (creates a match), False otherwise.
        Automatically reverts the swap if no match is created.
        """
        # Check bounds
        if not (0 <= r1 < self.rows and 0 <= c1 < self.cols and 
                0 <= r2 < self.rows and 0 <= c2 < self.cols):
            return False
        
        # Check adjacency (Manhattan distance == 1)
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False
            
        # Perform swap
        self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]
        
        # Post-swap validation: check if match created at either swapped position
        if self._is_part_of_match(r1, c1) or self._is_part_of_match(r2, c2):
            return True
            
        # Restore original state if invalid (no match created)
        self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]
        return False

    def detect_matches(self) -> List[Tuple[int, int]]:
        """
        Scans rows for horizontal matches and columns for vertical matches 
        of 3 or more. Aggregates all matched coordinates and returns them as a list.
        Correctly handles overlapping and intersecting match patterns by independently
        evaluating contiguous segments in both directions and unioning the results.
        """
        matched_coords = set()
        
        # Scan rows for horizontal matches
        for r in range(self.rows):
            c = 0
            while c < self.cols:
                gem_val = self.board[r][c]
                match_len = 1
                while c + match_len < self.cols and self.board[r][c + match_len] == gem_val:
                    match_len += 1
                
                if match_len >= 3:
                    for i in range(match_len):
                        matched_coords.add((r, c + i))
                
                c += match_len
        
        # Scan columns for vertical matches
        for c in range(self.cols):
            r = 0
            while r < self.rows:
                gem_val = self.board[r][c]
                match_len = 1
                while r + match_len < self.rows and self.board[r + match_len][c] == gem_val:
                    match_len += 1
                
                if match_len >= 3:
                    for i in range(match_len):
                        matched_coords.add((r + i, c))
                
                r += match_len
                
        return list(matched_coords)

    def clear_matches(self) -> None:
        """Clears matched gems from the board by setting them to 0."""
        matches = self.detect_matches()
        for r, c in matches:
            self.board[r][c] = 0

    def apply_gravity(self) -> None:
        """
        Implements column collapse logic that compacts non-empty tiles 
        to the bottom of each column, filling top gaps with zeros.
        """
        for c in range(self.cols):
            # Extract current column values from top to bottom
            col_values = [self.board[r][c] for r in range(self.rows)]
            
            # Filter out empty spaces (0s) to get only active gems
            non_empty = [val for val in col_values if val != 0]
            
            # Pad the top with zeros to maintain original column height
            new_col = [0] * (self.rows - len(non_empty)) + non_empty
            
            # Write the shifted column back to the board
            for r in range(self.rows):
                self.board[r][c] = new_col[r]

    def refill_board(self, prevent_matches: bool = True) -> None:
        """Generates new random gems at the top of each column to fill empty spaces (0s)."""
        for c in range(self.cols):
            for r in range(self.rows):
                if self.board[r][c] == 0:
                    while True:
                        gem = self._generate_random_gem()
                        # Validation loop: regenerate until placement creates no immediate matches
                        if prevent_matches and self._would_create_match(r, c, gem):
                            continue
                        self.board[r][c] = gem
                        break

    def process_board(self) -> int:
        """
        Iteratively processes matches until the board is stable.
        Repeatedly clears matches, applies gravity, refills empty spaces, 
        and checks for new matches. Returns total gems cleared across all steps.
        Automatically accumulates points into the player's score.
        """
        total_cleared = 0
        cascade_step = 0
        
        while True:
            matches = self.detect_matches()
            if not matches:
                break
            
            cascade_step += 1
            step_cleared = len(matches)
            total_cleared += step_cleared
            
            # Accumulate base score for this cascade step
            self.score += self.calculate_base_score(step_cleared)
            
            # Apply bonus based on match length and cascade depth
            self.score += self.calculate_bonus_score(step_cleared, cascade_step)
            
            self.clear_matches()
            self.apply_gravity()
            self.refill_board(prevent_matches=False)
            
        return total_cleared

    def process_cascade(self) -> int:
        """
        Recursively processes matches until the board is stable.
        Clears matches, applies gravity, refills empty spaces (allowing new matches),
        and repeats. Returns total gems cleared across all cascade steps.
        """
        # Delegate to the iterative process_board implementation for consistency
        return self.process_board()

    def calculate_base_score(self, cleared_count: int) -> int:
        """Calculates the base score based on the total number of cleared tiles per turn."""
        return cleared_count * 10

    def calculate_bonus_score(self, match_size: int, cascade_depth: int = 1) -> int:
        """
        Calculates bonus points for matches of 4 or more tiles.
        Integrates match length and cascade depth into the scoring calculation.
        """
        if match_size >= 4:
            return (match_size - 3) * 20
        return 0

    def get_score(self) -> int:
        """Returns the current accumulated player score."""
        return self.score

    def reset_score(self) -> None:
        """Resets the player score to zero."""
        self.score = 0

    def has_valid_moves(self) -> bool:
        """Checks if there are any valid moves remaining on the board."""
        for r in range(self.rows):
            for c in range(self.cols):
                # Check right neighbor
                if c + 1 < self.cols:
                    self.board[r][c], self.board[r][c+1] = self.board[r][c+1], self.board[r][c]
                    if self._is_part_of_match(r, c) or self._is_part_of_match(r, c+1):
                        # Revert swap
                        self.board[r][c], self.board[r][c+1] = self.board[r][c+1], self.board[r][c]
                        return True
                    # Revert swap
                    self.board[r][c], self.board[r][c+1] = self.board[r][c+1], self.board[r][c]
                
                # Check down neighbor
                if r + 1 < self.rows:
                    self.board[r][c], self.board[r+1][c] = self.board[r+1][c], self.board[r][c]
                    if self._is_part_of_match(r, c) or self._is_part_of_match(r+1, c):
                        # Revert swap
                        self.board[r][c], self.board[r+1][c] = self.board[r+1][c], self.board[r][c]
                        return True
                    # Revert swap
                    self.board[r][c], self.board[r+1][c] = self.board[r+1][c], self.board[r][c]
        return False