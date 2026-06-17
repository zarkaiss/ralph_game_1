import os
from src.game_logic import MatchThreeEngine
from src.renderer import render_board
from src.game_state import GameState


def parse_coordinates(user_input: str) -> tuple[int, int, int, int] | None:
    """
    Parses user input into four integer coordinates (r1, c1, r2, c2).
    Supports space or comma separation and strips surrounding parentheses.
    Returns a tuple of four integers if valid, otherwise None.
    """
    try:
        # Normalize delimiters to spaces for flexible input formats
        normalized = user_input.replace(',', ' ').replace('(', '').replace(')', '')
        parts = list(map(int, normalized.split()))
        
        if len(parts) != 4:
            return None
            
        return tuple(parts)
    except ValueError:
        return None


def clear_screen() -> None:
    """Clears the terminal screen using ANSI escape codes for broad compatibility and responsiveness."""
    print("\033[H\033[J", end="")


def main() -> None:
    """Runs the main game loop for the Match-3 puzzle."""
    engine = MatchThreeEngine(rows=8, cols=8)
    state = GameState(engine)
    
    print("=== Match-3 Puzzle Game ===")
    print("Enter swap coordinates as 'r1 c1 r2 c2' (0-indexed).")
    print("Tiles must be adjacent and the swap must create a match of 3+.")
    print("Type 'q' or 'quit' to exit.\n")
    
    while not state.game_over:
        # Check for exit conditions at the start of each turn
        if state.check_exit_conditions():
            break
            
        clear_screen()
        print(render_board(engine.get_board()))
        print(f"Turn: {state.turn_count} | Current Score: {engine.get_score()}")
        
        try:
            user_input = input("Your move: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGame exited.")
            break
            
        if user_input.lower() in ("q", "quit"):
            print("Thanks for playing!")
            break
            
        coords = parse_coordinates(user_input)
        if coords is None:
            print("Invalid input. Please enter exactly 4 integers (r1 c1 r2 c2).")
            if state.record_invalid_move():
                continue
            continue
            
        r1, c1, r2, c2 = coords
        
        # Validate bounds explicitly for clearer feedback before engine call
        if not (0 <= r1 < engine.rows and 0 <= c1 < engine.cols and 
                0 <= r2 < engine.rows and 0 <= c2 < engine.cols):
            print("Invalid move. Coordinates are out of bounds.\n")
            if state.record_invalid_move():
                continue
            continue
            
        success = engine.swap(r1, c1, r2, c2)
        
        if success:
            cleared_count = engine.process_cascade()
            new_score = engine.get_score()
            print(f"Valid move! Cleared {cleared_count} gems. New Score: {new_score}\n")
            state.record_valid_move()
        else:
            print("Invalid move. Ensure tiles are adjacent and create a match of 3+.\n")
            if state.record_invalid_move():
                continue

    # Final summary for playtesting verification
    clear_screen()
    print(render_board(engine.get_board()))
    print(f"Final Score: {engine.get_score()} | Turns Played: {state.turn_count}")
    print("Game Over. Thanks for playing!")


if __name__ == "__main__":
    main()