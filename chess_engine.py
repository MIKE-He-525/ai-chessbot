"""
Chess game engine
Implement core functions such as chessboard, rules, and move validation
"""
import chess
import chess.pgn
from typing import List, Optional, Tuple
import copy
from chess_evaluation import PIECE_VALUES, quick_evaluate

class ChessEngine:
    """Chess game engine"""
    
    def __init__(self):
        self.board = chess.Board()
        self.move_history = []
        
    def reset(self):
        """Reset the chessboard"""
        self.board = chess.Board()
        self.move_history = []
        
    def make_move(self, move: chess.Move) -> bool:
        """Execute the movement"""
        if move in self.board.legal_moves:
            self.board.push(move)
            self.move_history.append(move)
            return True
        return False
    
    def make_move_from_uci(self, uci_string: str) -> bool:
        """Execute movement from UCI string"""
        try:
            move = chess.Move.from_uci(uci_string)
            return self.make_move(move)
        except:
            return False
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get all legal moves"""
        return list(self.board.legal_moves)
    
    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.board.is_game_over()
    
    def get_result(self) -> Optional[str]:
        """Get the game result"""
        if not self.is_game_over():
            return None
        result = self.board.result()
        if result == "1-0":
            return "white"
        elif result == "0-1":
            return "black"
        else:
            return "draw"
    
    def is_check(self) -> bool:
        """Check if the current player is in check"""
        return self.board.is_check()
    
    def is_checkmate(self) -> bool:
        """Check if it's checkmate"""
        return self.board.is_checkmate()
    
    def is_stalemate(self) -> bool:
        """Check if it's a draw"""
        return self.board.is_stalemate()
    
    def get_turn(self) -> bool:
        """Get the current player (True = White, False = Black)"""
        return self.board.turn
    
    def get_fen(self) -> str:
        """Get the FEN string"""
        return self.board.fen()
    
    def get_board_copy(self):
        """Get a copy of the chessboard"""
        return copy.deepcopy(self.board)
    
    def undo_move(self):
        """Undo the previous move"""
        if self.move_history:
            self.board.pop()
            self.move_history.pop()
    
    def evaluate_position(self) -> float:
        """
        Evaluate the current situation (using a public evaluation function and adding additional evaluation items)
        Return: A positive number indicates White's advantage, and a negative number indicates Black's advantage
        """
        is_white_turn = self.board.turn == chess.WHITE
        score = quick_evaluate(self.board, from_white_perspective=True)
        
        piece_map = self.board.piece_map()
        center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
        
        for square, piece in piece_map.items():
            if square in center_squares:
                if piece.color == chess.WHITE:
                    score += 20
                else:
                    score -= 20
        
        if self.board.is_stalemate():
            if score > 0:
                score -= 1000
            elif score < 0:
                score += 1000
        
        if self.board.is_insufficient_material():
            if abs(score) > 100:
                score -= 500 if score > 0 else -500
        
        if self.board.is_repetition(3):
            if abs(score) > 200:
                score -= 200 if score > 0 else -200
        
        return score if is_white_turn else -score

