"""
//Chess AI Agent using Minimax w/Alpha-Beta Pruning
"""
import chess
import time
from pathlib import Path
from typing import Optional

#Piece-Square Tables (from White's perspective, flipped for Black)
#Higher = better quare for that piece

PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]
 
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]
 
ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]
 
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]
 
KING_MIDDLE_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]
 
KING_END_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
]
#Piece base values
PIECE_VALUES={
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

PIECE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_MIDDLE_TABLE
}

# Note: if trying to visual the board,
# DON'T FORGET TO SAVE THE chessVisual.ipynb FILE and allow overwrite
# if it is a fresh .ipynb file; otherwise proceed with whatever.
# also RERUN the python script so the overwrite permission is 
# active in the current game session 

VISUAL_NOTEBOOK = Path("chessVisual.ipynb")
VISUAL_WARNING_SHOWN = False


def visual(board: chess.Board) -> bool:
    """GD - notebook visualization that doesnt block CLI gameplay."""
    global VISUAL_WARNING_SHOWN

    try:
        import chess.svg
        import nbformat
        from nbconvert.preprocessors import ExecutePreprocessor
    except ImportError as exc:
        if not VISUAL_WARNING_SHOWN:
            print(f"  Notebook visualization disabled ({exc.name} is not installed).")
            VISUAL_WARNING_SHOWN = True
        return False

    try:
        svg_board = chess.svg.board(board=board)
        nb = nbformat.v4.new_notebook()
        nb["cells"] = [
            nbformat.v4.new_code_cell(
                "from IPython.display import SVG\n"
                f"svg_data = {svg_board!r}\n"
                "SVG(svg_data)"
            )
        ]

        with open(VISUAL_NOTEBOOK, "w", encoding="utf-8") as file_obj:
            nbformat.write(nb, file_obj)

        ep = ExecutePreprocessor(timeout=100, kernel_name="python3")
        ep.preprocess(nb, {"metadata": {"path": "./"}})

        with open(VISUAL_NOTEBOOK, "w", encoding="utf-8") as file_obj:
            nbformat.write(nb, file_obj)
        return True
    except Exception as exc:
        if not VISUAL_WARNING_SHOWN:
            print(f"  Notebook visualization disabled ({exc}).")
            VISUAL_WARNING_SHOWN = True
        return False

# Evaluation 
def is_endgame(board: chess.Board) -> bool:
    """Simple endgame detection: queens off or few pieces remain."""
    queens = len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
    minor = (
        len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK)) +
        len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.BLACK)) +
        len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK))
    )
    return queens == 0 or (queens == 2 and minor <= 2)
 
 
def piece_square_value(piece_type: int, square: chess.Square, color: chess.Color, endgame: bool) -> int:
    """Get the positional bonus for a piece on a given square."""
    table = KING_END_TABLE if (piece_type == chess.KING and endgame) else PIECE_TABLES[piece_type]
    # Tables are from White's perspective (a8=index 0, h1=index 63)
    if color == chess.WHITE:
        idx = chess.square_mirror(square)  # flip vertically for white
    else:
        idx = square
    return table[idx]
 
 
def evaluate(board: chess.Board) -> int:
    """
    Static board evaluation from White's perspective.
    Positive = good for White, Negative = good for Black.
    """
    if board.is_checkmate():
        return -100000 if board.turn == chess.WHITE else 100000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
 
    endgame = is_endgame(board)
    score = 0
 
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue
        value = PIECE_VALUES[piece.piece_type] + piece_square_value(piece.piece_type, square, piece.color, endgame)
        score += value if piece.color == chess.WHITE else -value
 
    # Mobility bonus (number of legal moves)
    if board.turn == chess.WHITE:
        white_moves = board.legal_moves.count()
        board.push(chess.Move.null())
        black_moves = board.legal_moves.count() if not board.is_game_over() else 0
        board.pop()
    else:
        black_moves = board.legal_moves.count()
        board.push(chess.Move.null())
        white_moves = board.legal_moves.count() if not board.is_game_over() else 0
        board.pop()
 
    score += (white_moves - black_moves) * 5
 
    return score
 
 
# Move Ordering (helps alpha-beta cut off more branches)
def move_score(board: chess.Board, move: chess.Move) -> int:
    """Heuristic score for move ordering (higher = try first)."""
    score = 0
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        if victim and attacker:
            score += 10 * PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type]
    if move.promotion:
        score += PIECE_VALUES[move.promotion]
    if board.gives_check(move):
        score += 50
    return score
 
 
def ordered_moves(board: chess.Board):
    return sorted(board.legal_moves, key=lambda m: move_score(board, m), reverse=True)
 
 
# Minimax with Alpha-Beta Pruning 
def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
    if depth == 0 or board.is_game_over():
        return evaluate(board)
 
    if maximizing:
        max_eval = -float('inf')
        for move in ordered_moves(board):
            board.push(move)
            eval_ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_)
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        min_eval = float('inf')
        for move in ordered_moves(board):
            board.push(move)
            eval_ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_)
            beta = min(beta, eval_)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval
 
 

# Chess Agent
class ChessAgent:
    """
    AI Chess Agent using Minimax with Alpha-Beta pruning.
 
    Args:
        depth (int): Search depth. Higher = stronger but slower.
                     Recommended: 2 (fast), 3 (balanced), 4 (strong), 5+ (slow)
        color (chess.Color): The color this agent plays as.
    """
 
    def __init__(self, depth: int = 3, color: chess.Color = chess.BLACK):
        self.depth = depth
        self.color = color
        self.nodes_searched = 0
 
    def choose_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Select the best move for the current position."""
        if board.is_game_over():
            return None
 
        self.nodes_searched = 0
        best_move = None
        maximizing = (self.color == chess.WHITE)
 
        best_eval = -float('inf') if maximizing else float('inf')
 
        for move in ordered_moves(board):
            board.push(move)
            self.nodes_searched += 1
            eval_ = minimax(board, self.depth - 1, -float('inf'), float('inf'), not maximizing)
            board.pop()
 
            if maximizing and eval_ > best_eval:
                best_eval = eval_
                best_move = move
            elif not maximizing and eval_ < best_eval:
                best_eval = eval_
                best_move = move
 
        return best_move
 
 

# CLI Game Loop 
BANNER = """
╔═══════════════════════════════════════╗
║           CHESS AI AGENT              ║
║   Minimax + Alpha-Beta Pruning        ║
╚═══════════════════════════════════════╝
"""
 
def print_board(board: chess.Board):
    """Pretty-print the board with rank/file labels."""
    print("\n   a b c d e f g h")
    print("  ─────────────────")
    rows = str(board).split("\n")
    for i, row in enumerate(rows):
        rank = 8 - i
        print(f" {rank}| {row} |{rank}")
    print("  ─────────────────")
    print("   a b c d e f g h\n")
 
 
def get_player_move(board: chess.Board) -> chess.Move:
    """Prompt the user for a move in UCI or SAN format."""
    while True:
        try:
            raw = input("  Your move (e.g. e2e4 or Nf3): ").strip()
            if not raw:
                continue
            # Try UCI first
            try:
                move = chess.Move.from_uci(raw)
                if move in board.legal_moves:
                    return move
            except ValueError:
                pass
            # Try SAN
            move = board.parse_san(raw)
            if move in board.legal_moves:
                return move
            print("  Illegal move. Try again.")
        except (ValueError, chess.IllegalMoveError, chess.InvalidMoveError, chess.AmbiguousMoveError) as e:
            print(f"  Invalid: {e}. Try again.")
        except KeyboardInterrupt:
            print("\n\nGame aborted.")
            exit()
 
 
def play_game():
    print(BANNER)

    # Setup
    print("Choose your color:")
    print("  [w] White (you go first)")
    print("  [b] Black (AI goes first)")
    choice = input("  -> ").strip().lower()
    player_color = chess.WHITE if choice == 'w' else chess.BLACK
    ai_color = chess.BLACK if player_color == chess.WHITE else chess.WHITE

    print("\nChoose difficulty:")
    print("  [1] Easy   (depth 2)")
    print("  [2] Medium (depth 3)")
    print("  [3] Hard   (depth 4)")
    diff = input("  -> ").strip()
    depth = {'1': 2, '2': 3, '3': 4}.get(diff, 3)

    agent = ChessAgent(depth=depth, color=ai_color)
    board = chess.Board()

    color_name = "White" if player_color == chess.WHITE else "Black"
    print(f"\n  You are playing as {color_name}. AI depth = {depth}.\n")
    print("  Enter moves in UCI (e2e4) or SAN (Nf3) format.")
    print("  Type 'quit' to exit, 'undo' to take back a move.\n")

    move_history = []
    
    visual(board)

    while not board.is_game_over():
        print_board(board)

        status = []
        if board.is_check():
            status.append("  CHECK!")
        turn_name = "White" if board.turn == chess.WHITE else "Black"
        who = "You" if board.turn == player_color else "AI"
        print(f"  Turn {board.fullmove_number} - {turn_name} to move ({who})")
        if status:
            print("  " + " | ".join(status))
 
        if board.turn == player_color:
            # Player's turn
            raw = input("  Your move: ").strip()
            if raw.lower() == 'quit':
                print("\n  Game abandoned. Goodbye!")
                return
            if raw.lower() == 'undo':
                if len(move_history) >= 2:
                    board.pop(); board.pop()
                    move_history = move_history[:-2]
                    print("  Last two moves undone.")
                else:
                    print("  Nothing to undo.")
                continue
            # Re-use get_player_move logic inline
            try:
                try:
                    move = chess.Move.from_uci(raw)
                    if move not in board.legal_moves:
                        raise ValueError("Illegal")
                except ValueError:
                    move = board.parse_san(raw)
            except Exception as e:
                print(f"  Invalid move: {e}\n")
                continue
 
            board.push(move)
            move_history.append(move)
            print(f"  You played: {move.uci()}\n")
 
        else:
            # AI's turn
            print("  AI is thinking...", end="", flush=True)
            t0 = time.time()
            ai_move = agent.choose_move(board)
            elapsed = time.time() - t0
 
            if ai_move is None:
                break
 
            san = board.san(ai_move)
            board.push(ai_move)
            visual(board)
            move_history.append(ai_move)
            print(f"\r  AI played: {san} ({elapsed:.2f}s, {agent.nodes_searched} nodes)\n")
 
    # Game over
    print_board(board)
    visual(board)
    result = board.result()
    outcome = board.outcome()
 
    print("  ═══════════════════════════════")
    if outcome:
        if outcome.winner is None:
            print("  Draw!")
        elif outcome.winner == player_color:
            print("  You win! Congratulations!")
        else:
            print("  AI wins. Better luck next time!")
        print(f"  Result: {result} | Reason: {outcome.termination.name}")
    print("  ═══════════════════════════════")
 
 
if __name__ == "__main__":
    play_game()