import pytest
from src.game_logic import MatchThreeEngine

class TestMatchThreeEngine:
    """
    Unit tests for the MatchThreeEngine class.
    These tests define the expected behavior and API of the game engine.
    """

    def setup_method(self):
        """Initialize a new engine instance before each test."""
        # Standard 8x8 grid initialization
        self.engine = MatchThreeEngine(rows=8, cols=8)

    def test_engine_initialization(self):
        """Verify the engine initializes with the correct grid dimensions."""
        board = self.engine.get_board()
        
        # Verify it is a two-dimensional list structure
        assert isinstance(board, list), "Board should be a list"
        assert len(board) == 8, "Board height should be 8"
        
        for row in board:
            assert isinstance(row, list), "Each row should be a list"
            assert len(row) == 8, "Board width should be 8"

    def test_board_populated_with_gems(self):
        """Verify the board is populated with valid gem identifiers."""
        board = self.engine.get_board()
        for row in board:
            for gem in row:
                # Assuming gems are represented by positive integers
                assert isinstance(gem, int), f"Gem should be an integer, got {type(gem)}"
                assert gem > 0, "Gem ID should be positive"

    def test_tile_values_within_range(self):
        """Verify all generated tiles contain integers between 1 and 5 inclusive."""
        board = self.engine.get_board()
        for row in board:
            for gem in row:
                assert 1 <= gem <= 5, f"Gem value {gem} is out of range [1, 5]"

    def test_swap_adjacent_cells(self):
        """Verify that adjacent cells can be swapped successfully when it creates a match."""
        # Setup to guarantee a vertical match after swapping (0,1) and (0,2)
        # We place identical gems vertically at col 1, rows 1 and 2.
        # After swap, board[0][1] will take the value from board[0][2], aligning with the vertical pair.
        self.engine.board[0][1] = 2
        self.engine.board[0][2] = 1
        self.engine.board[1][1] = 1
        self.engine.board[2][1] = 1
        
        val_1 = self.engine.get_board()[0][1]
        val_2 = self.engine.get_board()[0][2]

        # Perform swap -> should create a match at (0,1)
        success = self.engine.swap(0, 1, 0, 2)
        
        assert success is True, "Swap of adjacent cells should succeed when creating a match"
        
        # Verify values are swapped
        current_board = self.engine.get_board()
        assert current_board[0][1] == val_2
        assert current_board[0][2] == val_1

    def test_swap_non_adjacent_cells(self):
        """Verify that non-adjacent cells cannot be swapped."""
        # Attempt to swap cells that are not adjacent
        success = self.engine.swap(0, 0, 2, 2)
        
        assert success is False, "Swap of non-adjacent cells should fail"

    def test_swap_out_of_bounds(self):
        """Verify that swapping out-of-bounds coordinates fails."""
        # Attempt to swap with invalid indices
        success = self.engine.swap(0, 0, 10, 10)
        
        assert success is False, "Swap with out-of-bounds coordinates should fail"

    def test_boundary_checks_prevent_swapping_tiles_outside_grid_limits(self):
        """Verify boundary checks prevent swapping tiles outside the grid limits."""
        initial_board = [row[:] for row in self.engine.get_board()]
        
        # Test negative indices
        assert self.engine.swap(-1, 0, 0, 0) is False
        assert self.engine.swap(0, -1, 0, 0) is False
        
        # Test indices exactly at the boundary limit (8 for an 8x8 grid)
        assert self.engine.swap(8, 0, 0, 0) is False
        assert self.engine.swap(0, 8, 0, 0) is False
        
        # Test both coordinates out of bounds
        assert self.engine.swap(-5, -5, 10, 10) is False
        
        # Verify board state remains unchanged after failed swaps
        assert self.engine.get_board() == initial_board

    def test_boundary_checks_prevent_swapping_non_adjacent_tiles(self):
        """Verify boundary checks prevent swapping non-adjacent tiles."""
        initial_board = [row[:] for row in self.engine.get_board()]
        
        # Test diagonal adjacency (Manhattan distance > 1)
        assert self.engine.swap(0, 0, 1, 1) is False
        
        # Test same row, distance 2
        assert self.engine.swap(0, 0, 0, 2) is False
        
        # Test same column, distance 2
        assert self.engine.swap(0, 0, 2, 0) is False
        
        # Test far apart coordinates
        assert self.engine.swap(0, 0, 7, 7) is False
        
        # Verify board state remains unchanged after failed swaps
        assert self.engine.get_board() == initial_board

    def test_detect_horizontal_match(self):
        """Verify detection of horizontal matches."""
        # Reset board to a known state without any initial matches.
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                self.engine.board[r][c] = (r + c) % 5 + 1
                
        # Setup a row with exactly 3 identical gems at columns 2, 3, 4
        self.engine.board[0][1] = 1
        self.engine.board[0][2] = 5
        self.engine.board[0][3] = 5
        self.engine.board[0][4] = 5
        self.engine.board[0][5] = 2
        
        # Ensure vertical neighbors don't accidentally create a match
        # Explicitly set rows 1 and 2 to non-matching values to guarantee determinism
        for c in range(self.engine.cols):
            if c not in (2, 3, 4):
                self.engine.board[1][c] = 6  # Different from row 0 to prevent vertical matches
                self.engine.board[2][c] = 6
            else:
                self.engine.board[1][c] = 1 # Different from 5
                self.engine.board[2][c] = 1
                
        # Verify detection for the three matching tiles
        assert self.engine._is_part_of_match(0, 2) is True
        assert self.engine._is_part_of_match(0, 3) is True
        assert self.engine._is_part_of_match(0, 4) is True
        
        # Verify non-matching adjacent tiles are not detected
        assert self.engine._is_part_of_match(0, 1) is False
        assert self.engine._is_part_of_match(0, 5) is False

    def test_detect_vertical_match(self):
        """Verify detection of vertical matches."""
        # Reset board to a known state without any initial matches.
        # Using (r + c) % 5 + 1 guarantees no two adjacent cells share the same value,
        # preventing accidental horizontal or vertical matches during setup.
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                self.engine.board[r][c] = (r + c) % 5 + 1
                
        # Setup a column with exactly 3 identical gems at rows 0, 1, 2 in col 2
        self.engine.board[0][2] = 5
        self.engine.board[1][2] = 5
        self.engine.board[2][2] = 5
        self.engine.board[3][2] = 2 # Different value to ensure exactly 3 vertically
        
        # Verify detection for the three matching tiles
        assert self.engine._is_part_of_match(0, 2) is True
        assert self.engine._is_part_of_match(1, 2) is True
        assert self.engine._is_part_of_match(2, 2) is True
        
        # Verify non-matching adjacent tiles are not detected
        assert self.engine._is_part_of_match(3, 2) is False
        assert self.engine._is_part_of_match(0, 1) is False
        assert self.engine._is_part_of_match(0, 3) is False

    def test_clear_matches(self):
        """Verify that matched gems are cleared from the board."""
        # Reset board to a safe state without matches
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                self.engine.board[r][c] = (r + c) % 5 + 1
                
        # Setup a horizontal match of 3 at row 2, cols 1-3 with value 4
        self.engine.board[2][1] = 4
        self.engine.board[2][2] = 4
        self.engine.board[2][3] = 4
        
        # Clear matches
        self.engine.clear_matches()
        
        # Verify matched tiles are set to 0
        assert self.engine.board[2][1] == 0
        assert self.engine.board[2][2] == 0
        assert self.engine.board[2][3] == 0
        
        # Verify non-matched tiles remain unchanged (e.g., row 0, col 0)
        assert self.engine.board[0][0] == 1

    def test_gravity_effect(self):
        """Verify that gems drop down to fill empty spaces after clearing."""
        # Reset board to a known state with zeros
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                self.engine.board[r][c] = 0
                
        # Place gems at various heights with gaps above them
        self.engine.board[2][0] = 1
        self.engine.board[4][0] = 2
        self.engine.board[1][1] = 3
        self.engine.board[5][1] = 4
        
        self.engine.apply_gravity()
        
        # Column 0: gems should drop to the bottom (rows 6 and 7)
        assert self.engine.board[6][0] == 1
        assert self.engine.board[7][0] == 2
        for r in range(6):
            assert self.engine.board[r][0] == 0
            
        # Column 1: gems should drop to the bottom (rows 6 and 7)
        assert self.engine.board[6][1] == 3
        assert self.engine.board[7][1] == 4
        for r in range(6):
            assert self.engine.board[r][1] == 0
            
        # Ensure other columns remain empty
        for r in range(self.engine.rows):
            for c in range(2, self.engine.cols):
                assert self.engine.board[r][c] == 0

    def test_refill_board(self):
        """Verify that new gems are generated at the top of the board."""
        # Reset board to a known state with zeros at the top after gravity
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                self.engine.board[r][c] = 0
                
        # Place some gems at the bottom
        for c in range(self.engine.cols):
            self.engine.board[7][c] = (c % 5) + 1
            
        # Apply gravity (zeros stay at top, gems at bottom)
        self.engine.apply_gravity()
        
        # Verify zeros are at the top before refill
        for r in range(7):
            assert self.engine.board[r][0] == 0
            
        # Refill board
        self.engine.refill_board()
        
        # Verify all cells now contain valid gem IDs (1-5)
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                assert 1 <= self.engine.board[r][c] <= 5, \
                    f"Cell ({r}, {c}) should be filled with a valid gem ID after refill"
                    
        # Verify bottom row gems remain unchanged
        for c in range(self.engine.cols):
            assert self.engine.board[7][c] == (c % 5) + 1

    def test_no_initial_matches(self):
        """Assert that no horizontal or vertical matches of 3 or more exist upon initialization."""
        board = self.engine.get_board()
        
        # Check for horizontal matches of length >= 3
        for r in range(self.engine.rows):
            for c in range(self.engine.cols - 2):
                assert not (board[r][c] == board[r][c+1] == board[r][c+2]), \
                    f"Found horizontal match at ({r}, {c})"
                    
        # Check for vertical matches of length >= 3
        for r in range(self.engine.rows - 2):
            for c in range(self.engine.cols):
                assert not (board[r][c] == board[r+1][c] == board[r+2][c]), \
                    f"Found vertical match at ({r}, {c})"

    def test_swap_horizontally_adjacent_tiles(self):
        """Verify successful swapping of two horizontally adjacent tiles that creates a match."""
        r, c = 3, 4
        # Setup to guarantee a vertical match after swap (simpler to construct reliably)
        self.engine.board[r][c] = 2
        self.engine.board[r][c + 1] = 1
        self.engine.board[r + 1][c] = 1
        self.engine.board[r + 2][c] = 1
        
        val_left = self.engine.get_board()[r][c]
        val_right = self.engine.get_board()[r][c + 1]
        
        success = self.engine.swap(r, c, r, c + 1)
        assert success is True, "Swapping horizontally adjacent tiles should succeed when creating a match"
        
        board = self.engine.get_board()
        assert board[r][c] == val_right, "Left tile should now hold the right tile's value"
        assert board[r][c + 1] == val_left, "Right tile should now hold the left tile's value"

    def test_swap_vertically_adjacent_tiles(self):
        """Verify successful swapping of two vertically adjacent tiles that creates a match."""
        r, c = 3, 4
        # Setup to guarantee a horizontal match after swap
        self.engine.board[r][c] = 2
        self.engine.board[r + 1][c] = 1
        self.engine.board[r][c - 1] = 1
        self.engine.board[r][c + 1] = 1
        
        val_top = self.engine.get_board()[r][c]
        val_bottom = self.engine.get_board()[r + 1][c]
        
        success = self.engine.swap(r, c, r + 1, c)
        assert success is True, "Swapping vertically adjacent tiles should succeed when creating a match"
        
        board = self.engine.get_board()
        assert board[r][c] == val_bottom, "Top tile should now hold the bottom tile's value"
        assert board[r + 1][c] == val_top, "Bottom tile should now hold the top tile's value"

    def test_swap_reverts_when_no_match(self):
        """Verify that a swap automatically reverts if it does not produce a match of 3 or more."""
        # Manually configure a local area to guarantee no match will form upon swapping
        self.engine.board[0][0] = 1
        self.engine.board[0][1] = 2
        self.engine.board[0][2] = 3
        self.engine.board[1][0] = 4
        self.engine.board[1][1] = 5
        
        initial_board = [row[:] for row in self.engine.get_board()]
        
        # Attempt swap between (0,0) and (0,1)
        success = self.engine.swap(0, 0, 0, 1)
        
        assert success is False, "Swap should fail when no match is created"
        current_board = self.engine.get_board()
        assert current_board == initial_board, "Board should revert to original state if swap doesn't create a match"

    def test_detect_matches_length_4_and_5(self):
        """Verify detection of horizontal matches of length 4 and vertical matches of length 5."""
        # Reset board to a safe state without matches
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                self.engine.board[r][c] = (r + c) % 5 + 1
                
        # Setup horizontal match of length 4 at row 3, cols 1-4 with value 2
        self.engine.board[3][1] = 2
        self.engine.board[3][2] = 2
        self.engine.board[3][3] = 2
        self.engine.board[3][4] = 2
        
        # Setup vertical match of length 5 at col 7, rows 0-4 with value 5
        self.engine.board[0][7] = 5
        self.engine.board[1][7] = 5
        self.engine.board[2][7] = 5
        self.engine.board[3][7] = 5
        self.engine.board[4][7] = 5
        
        # Verify _is_part_of_match for length 4 horizontal
        assert self.engine._is_part_of_match(3, 1) is True
        assert self.engine._is_part_of_match(3, 2) is True
        assert self.engine._is_part_of_match(3, 3) is True
        assert self.engine._is_part_of_match(3, 4) is True
        
        # Verify _is_part_of_match for length 5 vertical
        assert self.engine._is_part_of_match(0, 7) is True
        assert self.engine._is_part_of_match(1, 7) is True
        assert self.engine._is_part_of_match(2, 7) is True
        assert self.engine._is_part_of_match(3, 7) is True
        assert self.engine._is_part_of_match(4, 7) is True
        
        # Verify detect_matches returns all coordinates for these matches
        matched = self.engine.detect_matches()
        expected_coords = {
            (3, 1), (3, 2), (3, 3), (3, 4),
            (0, 7), (1, 7), (2, 7), (3, 7), (4, 7)
        }
        assert set(matched) == expected_coords, f"Expected {expected_coords}, got {set(matched)}"

    def test_new_random_tiles_populate_top_rows_after_collapse(self):
        """Verify new random tiles populate the top rows after collapse."""
        # Reset board to a known state without matches
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                self.engine.board[r][c] = (r + c) % 5 + 1
                
        # Create a vertical match at the bottom of column 0 to trigger collapse
        self.engine.board[5][0] = 3
        self.engine.board[6][0] = 3
        self.engine.board[7][0] = 3
        
        # Clear matches -> sets (5,0), (6,0), (7,0) to 0
        self.engine.clear_matches()
        
        # Apply gravity -> gems above drop down, top becomes 0
        self.engine.apply_gravity()
        
        # Verify zeros are at the top of column 0 before refill
        assert self.engine.board[0][0] == 0
        assert self.engine.board[1][0] == 0
        assert self.engine.board[2][0] == 0
        
        # Refill board -> should populate zeros with new random gems (1-5)
        self.engine.refill_board()
        
        # Verify top rows are now populated with valid gem IDs
        for r in range(self.engine.rows):
            assert 1 <= self.engine.board[r][0] <= 5, f"Cell ({r}, 0) should contain a valid gem ID after refill"
            
        # Verify other columns remain unchanged and valid
        for r in range(self.engine.rows):
            for c in range(1, self.engine.cols):
                assert 1 <= self.engine.board[r][c] <= 5

    def test_recursive_cascade_processing(self):
        """Verify recursive processing when tile refilling triggers cascading chain reactions."""
        # Setup board with a known state
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                self.engine.board[r][c] = (r + c) % 5 + 1
                
        # Create initial vertical match of 3 at col 0, rows 5-7
        self.engine.board[5][0] = 1
        self.engine.board[6][0] = 1
        self.engine.board[7][0] = 1
        
        cascade_rounds = [0]
        
        def mock_refill(prevent_matches=True):
            cascade_rounds[0] += 1
            if cascade_rounds[0] == 1:
                # First refill: create a horizontal match at row 0 to trigger round 2.
                # Using value 2 avoids accidental collision with existing board values 
                # that would extend the match beyond length 3.
                self.engine.board[0][0] = 2
                self.engine.board[0][1] = 2
                self.engine.board[0][2] = 2
            # Fill all remaining zeros with a checkerboard pattern that avoids creating new matches.
            # This guarantees the recursion terminates after exactly two cascade rounds.
            for c in range(self.engine.cols):
                for r in range(self.engine.rows):
                    if self.engine.board[r][c] == 0:
                        self.engine.board[r][c] = (r + c) % 2 + 1

        self.engine.refill_board = mock_refill
        
        # Process cascade
        total_cleared = self.engine.process_cascade()
        
        # First round clears 3, second round clears 3. Total should be 6.
        assert total_cleared == 6, f"Expected 6 cleared gems across two cascade rounds, got {total_cleared}"
        
        # Verify board is stable (no matches left)
        assert len(self.engine.detect_matches()) == 0, "Board should be stable after cascade processing"

    def test_calculate_base_score(self):
        """Verify that base score is calculated correctly based on the total number of cleared tiles per turn."""
        # Base score calculation: 10 points per cleared tile
        assert self.engine.calculate_base_score(3) == 30
        assert self.engine.calculate_base_score(5) == 50
        assert self.engine.calculate_base_score(12) == 120
        assert self.engine.calculate_base_score(0) == 0

    def test_bonus_point_allocation_for_four_tile_matches(self):
        """Verify bonus point allocation for 4-tile matches."""
        # A 4-tile match should yield a bonus of 20 points (1 extra tile * 20)
        assert self.engine.calculate_bonus_score(4) == 20
        # Matches of 3 or fewer should yield no bonus
        assert self.engine.calculate_bonus_score(3) == 0
        assert self.engine.calculate_bonus_score(2) == 0
        # Verify bonus scales for larger matches (e.g., 5 tiles -> 40 bonus)
        assert self.engine.calculate_bonus_score(5) == 40

    def test_bonus_point_allocation_for_cascade_chain_reactions(self):
        """Verify bonus point allocation for cascade chain reactions."""
        # Setup a deterministic board state to guarantee predictable cascade behavior
        for r in range(self.engine.rows):
            for c in range(self.engine.cols):
                self.engine.board[r][c] = (r + c) % 5 + 1
                
        # Create initial vertical match of 4 at col 0, rows 4-7
        self.engine.board[4][0] = 2
        self.engine.board[5][0] = 2
        self.engine.board[6][0] = 2
        self.engine.board[7][0] = 2
        
        initial_score = self.engine.get_score()
        
        # Track cascade steps and mock refill to trigger a second match of 4 in the next step
        steps = [0]
        def controlled_refill(prevent_matches=True):
            steps[0] += 1
            if steps[0] == 1:
                # After gravity, top rows are empty. Place horizontal match of 4 at row 0.
                self.engine.board[0][2] = 3
                self.engine.board[0][3] = 3
                self.engine.board[0][4] = 3
                self.engine.board[0][5] = 3
            # Fill remaining zeros safely with a pattern that avoids accidental matches
            for c in range(self.engine.cols):
                for r in range(self.engine.rows):
                    if self.engine.board[r][c] == 0:
                        self.engine.board[r][c] = (r + c) % 2 + 1
                        
        self.engine.refill_board = controlled_refill
        
        # Process cascade
        self.engine.process_cascade()
        
        final_score = self.engine.get_score()
        delta = final_score - initial_score
        
        # Expected scoring breakdown:
        # Step 1 clears 4 tiles -> Base: 40, Bonus: (4-3)*20 = 20
        # Step 2 clears 4 tiles -> Base: 40, Bonus: (4-3)*20 = 20
        # Total expected delta: 80 (base) + 40 (bonus) = 120
        assert delta == 120, f"Expected score delta of 120 across cascade steps, got {delta}"