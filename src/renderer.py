def render_board(board: list[list[int]]) -> str:
    """
    Renders the current game board state as a formatted text string.
    Uses box-drawing characters for borders and maps gem IDs to distinct symbols.
    """
    if not board or not board[0]:
        return ""
        
    cols = len(board[0])
    
    # Gem symbol mapping for visual distinction
    gem_map = {
        1: "R", 2: "O", 3: "Y", 4: "G", 5: "B"
    }
    
    lines = []
    # Top border
    lines.append("┌" + "──" * cols + "┐")
    
    for row in board:
        row_str = "│"
        for val in row:
            if val == 0:
                row_str += "  │"
            else:
                symbol = gem_map.get(val, str(val))
                row_str += f"{symbol} │"
        lines.append(row_str)
        
    # Bottom border
    lines.append("└" + "──" * cols + "┘")
    
    return "\n".join(lines)