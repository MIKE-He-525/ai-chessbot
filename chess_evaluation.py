"""
Chess Evaluation Function Tool Module
Extract common evaluation logic for use by various AI classes
"""
import chess
from typing import Dict


PIECE_VALUES: Dict[int, int] = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}


def quick_evaluate(board: chess.Board, from_white_perspective: bool = True) -> float:
    """
    Quick Evaluation Function (Optimized Version: Avoid Using the Engine)
    
    Args:
        board: The state of the chessboard
        from_white_perspective: Whether to evaluate from the white player's perspective (True = positive number indicates white's advantage)
    
    Returns:
        Evaluation score (from the specified perspective)
    """

    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -100000 if from_white_perspective else 100000
        else:
            return 100000 if from_white_perspective else -100000
    
    score = 0
    is_white_turn = board.turn == chess.WHITE
    
    piece_map = board.piece_map()
    for square, piece in piece_map.items():
        value = PIECE_VALUES[piece.piece_type]
        if piece.color == chess.WHITE:
            score += value
        else:
            score -= value
    

    current_moves = len(list(board.legal_moves))
    temp_board = board.copy()
    temp_board.turn = not temp_board.turn
    opponent_moves = len(list(temp_board.legal_moves))

    if is_white_turn:
        mobility_diff = current_moves - opponent_moves
    else:
        mobility_diff = opponent_moves - current_moves
    score += mobility_diff * 2
    
    if board.is_check():
        if is_white_turn:
            score -= 50
        else:
            score += 50
    
    if from_white_perspective:
        return score
    else:
        return -score


def move_priority(board: chess.Board, move: chess.Move) -> int:
    """
    Calculate movement priority (for movement sorting)
    
    Args:
        board: board state
        move: movement
    
    Returns:
        priority score (the higher, the higher the priority)
    """
    priority = 0
   
    if board.is_capture(move):
        captured_piece = board.piece_at(move.to_square)
        if captured_piece:
            victim_value = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 0}
            priority += victim_value.get(captured_piece.piece_type, 0) * 100
    if board.gives_check(move):
        priority += 50
    return priority


def sort_moves_by_priority(board: chess.Board, moves: list) -> list:
    """
    Sort moves by priority
    
    Args:
        board: the state of the chessboard
        moves: list of moves
    
    Returns:
        sorted list of moves
    """
    return sorted(moves, key=lambda m: move_priority(board, m), reverse=True)

