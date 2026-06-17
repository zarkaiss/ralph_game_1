class GameState:
    """Manages game flow, turns, invalid move limits, and exit conditions."""
    
    def __init__(self, engine):
        self.engine = engine
        self.turn_count = 0
        self.invalid_moves = 0
        self.max_invalid_per_turn = 3
        self.game_over = False

    def record_valid_move(self) -> None:
        """Records a successful move, increments turn count, and resets invalid move counter."""
        self.turn_count += 1
        self.invalid_moves = 0

    def record_invalid_move(self) -> bool:
        """
        Records an invalid move. If the limit is reached, skips the turn.
        Returns True if the turn was skipped due to too many invalid moves.
        """
        self.invalid_moves += 1
        if self.invalid_moves >= self.max_invalid_per_turn:
            print(f"Too many invalid moves ({self.max_invalid_per_turn}). Turn skipped.")
            self.turn_count += 1
            self.invalid_moves = 0
            return True
        return False

    def check_exit_conditions(self) -> bool:
        """Checks if the game should end due to lack of valid moves."""
        if not self.engine.has_valid_moves():
            print("No more valid moves available! Game Over.")
            self.game_over = True
            return True
        return False