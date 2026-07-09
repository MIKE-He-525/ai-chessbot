"""
AI player realization
It includes AI algorithms of multiple difficulty levels
Simplify the code by using public evaluation functions
"""
import chess
import random
import math
from typing import Dict, List, Optional, Tuple
from chess_engine import ChessEngine
from chess_evaluation import quick_evaluate, move_priority, sort_moves_by_priority, PIECE_VALUES
import time

class AIPlayer:
    """AI player base class"""
    
    def __init__(self, name: str, color: bool):
        self.name = name
        self.color = color  # True=白方, False=黑方
        self.engine = ChessEngine()
        
    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Get the next move"""
        raise NotImplementedError
        
    def reset(self):
        """Reset the AI status"""
        self.engine.reset()

class RandomAI(AIPlayer):
    """Random AI - Beginner Difficulty"""
    
    def __init__(self, color: bool):
        super().__init__("Random AI (Beginner)", color)
        
    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Randomly select a legal move"""
        legal_moves = list(board.legal_moves)
        if legal_moves:
            return random.choice(legal_moves)
        return None

class GreedyAI(AIPlayer):
    """Greedy AI - Intermediate Difficulty"""
    
    def __init__(self, color: bool):
        super().__init__("Greedy AI (Intermediate)", color)
        
    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Select the move that best assesses the current situation (using the public evaluation function)"""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        maximizing = board.turn
        best_move = None
        best_score = -float('inf') if maximizing else float('inf')
        
        for move in legal_moves:
            board.push(move)

            score = quick_evaluate(board, from_white_perspective=True)
            board.pop()
            
            if maximizing: 
                if score > best_score:
                    best_score = score
                    best_move = move
            else:  
                if score < best_score:
                    best_score = score
                    best_move = move
        
        return best_move if best_move else legal_moves[0]

class MinimaxAI(AIPlayer):
    """Minimax AI - Advanced Difficulty"""
    
    def __init__(self, color: bool, depth: int = 3):
        super().__init__(f"Minimax AI (Advanced-Depth {depth})", color)
        self.depth = depth
        self.transposition_table: Dict[str, Tuple[int, float]] = {}
        self.max_tt_size = 10000  
    
    
    def _limit_transposition_table(self):
        """Limit the size of the transposition table"""
        if len(self.transposition_table) > self.max_tt_size:
            items = list(self.transposition_table.items())
            self.transposition_table = dict(items[len(items) // 2:])
    
    def minimax_ab(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool
    ) -> float:
        """Minimax with alpha-beta pruning and transposition table"""
        fen = board.fen()
        if fen in self.transposition_table:
            stored_depth, stored_value = self.transposition_table[fen]
            if stored_depth >= depth:
                return stored_value
        
        if depth == 0 or board.is_game_over():
            value = quick_evaluate(board, from_white_perspective=board.turn)
            
            if len(self.transposition_table) < self.max_tt_size:
                self.transposition_table[fen] = (depth, value)
            return value
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
           
            value = quick_evaluate(board, from_white_perspective=board.turn)
            return value
        
       
        legal_moves = sort_moves_by_priority(board, legal_moves)
        
        if maximizing:
            value = -float("inf")
            for move in legal_moves:
                board.push(move)
                score = self.minimax_ab(board, depth - 1, alpha, beta, False)
                board.pop()
                value = max(value, score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  
        else:
            value = float("inf")
            for move in legal_moves:
                board.push(move)
                score = self.minimax_ab(board, depth - 1, alpha, beta, True)
                board.pop()
                value = min(value, score)
                beta = min(beta, value)
                if alpha >= beta:
                    break  
        
        
        if len(self.transposition_table) < self.max_tt_size:
            self.transposition_table[fen] = (depth, value)
        else:
            self._limit_transposition_table()
        return value
    
    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Use the improved Minimax to get the best move"""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        
        best_move = None
        
        maximizing = board.turn
        best_score = -float("inf") if maximizing else float("inf")
        alpha = -float("inf")
        beta = float("inf")
        
        
        legal_moves = sort_moves_by_priority(board, legal_moves)
        
        
        for move in legal_moves:
            board.push(move)
            
            score = self.minimax_ab(board, self.depth - 1, alpha, beta, not maximizing)
            board.pop()
            
            if maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                    alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                    beta = min(beta, score)
            
            
            if beta <= alpha:
                break
        
        return best_move if best_move else legal_moves[0]

class AlphaBetaAI(AIPlayer):
    """Alpha-Beta Pruning AI - Advanced Difficulty"""
    
    def __init__(self, color: bool, depth: int = 4):
        super().__init__(f"Alpha-Beta AI (Advanced-Depth {depth})", color)
        self.depth = depth
    
    def alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Alpha-Beta Pruning Algorithm (using a public evaluation function)"""
        if depth == 0 or board.is_game_over():
            
            score = quick_evaluate(board, from_white_perspective=True)
            return score
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            
            score = quick_evaluate(board, from_white_perspective=True)
            return score
        
        
        legal_moves = sort_moves_by_priority(board, legal_moves)
        
        if maximizing:
            max_eval = -float('inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self.alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self.alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  
            return min_eval
    
    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Obtain the best move using Alpha-Beta pruning (using public functions)"""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        best_move = None
        
        maximizing = board.turn
        best_score = -float('inf') if maximizing else float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        
        legal_moves = sort_moves_by_priority(board, legal_moves)
        
        
        for move in legal_moves:
            board.push(move)
            
            score = self.alpha_beta(board, self.depth - 1, alpha, beta, not maximizing)
            board.pop()
            
            if maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                    alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                    beta = min(beta, score)
            
            
            if beta <= alpha:
                break
        
        return best_move if best_move else legal_moves[0]

class NegamaxAI(AIPlayer):
    """Obtain the best move using Alpha-Beta pruning (using public functions)"""
    
    def __init__(self, color: bool, depth: int = 4):
        super().__init__(f"Negamax AI (Advanced-Depth {depth})", color)
        self.depth = depth
        
    def negamax(self, board: chess.Board, depth: int, alpha: float, beta: float, color: int) -> float:
        """Negamax algorithm (with Alpha-Beta pruning, using a common evaluation function)"""
        if depth == 0 or board.is_game_over():
            
            score = quick_evaluate(board, from_white_perspective=True)
            return color * score
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            
            score = quick_evaluate(board, from_white_perspective=True)
            return color * score
        
        
        legal_moves = sort_moves_by_priority(board, legal_moves)
        
        best_value = -float('inf')
        for move in legal_moves:
            board.push(move)
            value = -self.negamax(board, depth - 1, -beta, -alpha, -color)
            board.pop()
            best_value = max(best_value, value)
            alpha = max(alpha, value)
            if alpha >= beta:
                break  
        return best_value
    
    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Use Negamax to get the best move (using public functions)"""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        best_move = None
        alpha = -float('inf')
        beta = float('inf')
        
        color = 1 if board.turn else -1
        
        
        legal_moves = sort_moves_by_priority(board, legal_moves)
        
        
        for move in legal_moves:
            board.push(move)
            
            value = -self.negamax(board, self.depth - 1, -beta, -alpha, -color)
            board.pop()
            
            if value > alpha:
                alpha = value
                best_move = move
            
            
            if beta <= alpha:
                break
        
        return best_move if best_move else legal_moves[0]

class AdvancedAI(AIPlayer):
    """
    Advanced AI - Alpha-Beta Pruning Algorithm with Enhanced Evaluation Function (Dual-Mode Optimization Version)
    
    Features:
    - Dual-mode design:
      * Game mode (test_mode=False): Fast response, depth 5, time budget 1.5 seconds
      * Test mode (test_mode=True): Full performance, depth 7, time budget 5 seconds
    - Iterative deepening: Search gradually from shallow to deep to find the optimal solution within the time budget
    - Time budget control: Limit the thinking time per step to avoid slow response
    - Enhanced evaluation function: Advanced heuristics such as position value, pawn position, king safety, etc.
    - Optimized move ordering: Prioritize captures/checks to improve pruning efficiency
    - Transposition table: Cache the results of already searched positions
    - Quiescence search: Continue searching for captures and checks when depth is 0 to avoid the horizon effect
    """
    
    def __init__(self, color: bool, depth: int = 7, test_mode: bool = False):
        """
        Initialize AdvancedAI
        
        Args:
            color: The color of the chess piece (True = white, False = black)
            depth: Maximum search depth (only used when test_mode=False; when test_mode=True, it will be automatically set to a higher value)
            test_mode: Whether it is test mode
                - False (game mode): Quick response, depth 5, time budget 1.5 seconds
                - True (test mode): Full performance, depth 7, time budget 5 seconds
        """
        
        if test_mode:
            
            actual_depth = depth if depth >= 7 else 7
            time_budget = 5000  
            mode_name = "Test"
        else:
            
            actual_depth = min(depth, 5)  
            time_budget = 1500  
            mode_name = "Game"
        
        super().__init__(f"Advanced AI ({mode_name}-Depth {actual_depth})", color)
        self.max_depth = actual_depth
        self.time_budget_ms = time_budget
        self.test_mode = test_mode
        
        if not hasattr(AdvancedAI, "_shared_tt"):
            AdvancedAI._shared_tt = {}
        self.transposition_table = AdvancedAI._shared_tt
        self.max_tt_size = 100000
    
    def _advanced_evaluate(self, board: chess.Board, include_mobility: bool = False) -> float:
        """Advanced evaluation function: Using enhanced traditional heuristic evaluation (optimized version, which does not calculate mobility by default to improve speed)"""
        is_white_turn = board.turn == chess.WHITE
        
        
        if board.is_checkmate():
            return -1000000 if is_white_turn else 1000000
        
        
        score = quick_evaluate(board, from_white_perspective=True)
        
        
        center_squares = [chess.E4, chess.E5, chess.D4, chess.D5]
        extended_center = [chess.C3, chess.C4, chess.C5, chess.C6,
                          chess.D3, chess.D6, chess.E3, chess.E6,
                          chess.F3, chess.F4, chess.F5, chess.F6]
        
        piece_map = board.piece_map()
        white_pieces = 0
        black_pieces = 0
        
        for square, piece in piece_map.items():
            value = 0  
            
            
            if square in center_squares:
                value += 20
            elif square in extended_center:
                value += 10
            
            
            if piece.piece_type == chess.PAWN:
                if piece.color == chess.WHITE:
                    value += chess.square_rank(square) * 8  
                else:
                    value += (7 - chess.square_rank(square)) * 8
            
            
            if piece.piece_type == chess.KING:
                if piece.color == chess.WHITE:
                    
                    if chess.square_rank(square) <= 1:
                        value += 30
                else:
                    if chess.square_rank(square) >= 6:
                        value += 30
            
            if piece.color == chess.WHITE:
                score += value
                white_pieces += 1
            else:
                score -= value
                black_pieces += 1
        
        
        if board.is_check():
            score -= 100 if is_white_turn else -100
        
        
        if board.has_kingside_castling_rights(chess.WHITE):
            score += 20
        if board.has_queenside_castling_rights(chess.WHITE):
            score += 15
        if board.has_kingside_castling_rights(chess.BLACK):
            score -= 20
        if board.has_queenside_castling_rights(chess.BLACK):
            score -= 15
        
        
        material_diff = white_pieces - black_pieces
        if abs(material_diff) > 2:  
            score += material_diff * 50
        
        return score if is_white_turn else -score
    
    
    def _limit_transposition_table(self):
        """Limit the size of the transposition table and delete the oldest entries"""
        if len(self.transposition_table) > self.max_tt_size:
            
            items = list(self.transposition_table.items())
            self.transposition_table = dict(items[len(items) // 2:])
    
    def _quiescence_search(self, board: chess.Board, alpha: float, beta: float, maximizing: bool, depth: int = 3) -> float:
        """Static search: Continue searching for captures and checks when the depth is 0 to avoid the horizon effect."""
        
        stand_pat = self._advanced_evaluate(board, include_mobility=False)
        
        if depth <= 0:
            return stand_pat
        
        
        if maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)
        
        
        legal_moves = [m for m in board.legal_moves if board.is_capture(m) or board.gives_check(m)]
        if not legal_moves:
            return stand_pat
        
        
        legal_moves = sort_moves_by_priority(board, legal_moves)
        
        if maximizing:
            for move in legal_moves:
                board.push(move)
                score = self._quiescence_search(board, alpha, beta, False, depth - 1)
                board.pop()
                stand_pat = max(stand_pat, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return stand_pat
        else:
            for move in legal_moves:
                board.push(move)
                score = self._quiescence_search(board, alpha, beta, True, depth - 1)
                board.pop()
                stand_pat = min(stand_pat, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return stand_pat
    
    def alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool, start_time: float = None, time_limit: float = None) -> float:
        """Alpha-Beta Pruning Algorithm (using an enhanced evaluation function and supporting time control)"""
        
        if start_time and time_limit:
            if time.time() - start_time > time_limit:
                raise TimeoutError("Time limit exceeded")
        
        
        board_fen = board.fen()
        if board_fen in self.transposition_table:
            stored_depth, stored_score = self.transposition_table[board_fen]
            if stored_depth >= depth:
                return stored_score
        
        if depth == 0 or board.is_game_over():
            
            score = self._quiescence_search(board, alpha, beta, maximizing, depth=2)
            
            if len(self.transposition_table) < self.max_tt_size:
                self.transposition_table[board_fen] = (0, score)
            return score
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            score = self._advanced_evaluate(board, include_mobility=False)
            return score
        
        
        legal_moves = sort_moves_by_priority(board, legal_moves)
        
        if maximizing:
            max_eval = -float('inf')
            for move in legal_moves:
                board.push(move)
                try:
                    eval_score = self.alpha_beta(board, depth - 1, alpha, beta, False, start_time, time_limit)
                except TimeoutError:
                    board.pop()
                    raise
                board.pop()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  
            
            if len(self.transposition_table) < self.max_tt_size:
                self.transposition_table[board_fen] = (depth, max_eval)
            else:
                self._limit_transposition_table()
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                try:
                    eval_score = self.alpha_beta(board, depth - 1, alpha, beta, True, start_time, time_limit)
                except TimeoutError:
                    board.pop()
                    raise
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  
            
            if len(self.transposition_table) < self.max_tt_size:
                self.transposition_table[board_fen] = (depth, min_eval)
            else:
                self._limit_transposition_table()
            return min_eval
    
    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Obtain the best move using iterative deepening with Alpha-Beta pruning (to optimize response time)"""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        maximizing = board.turn
        
        legal_moves = sort_moves_by_priority(board, legal_moves)
        
        start_time = time.time()
        time_limit = self.time_budget_ms / 1000.0  
        
        best_move = legal_moves[0]  
        best_score = -float('inf') if maximizing else float('inf')
        
        for current_depth in range(1, self.max_depth + 1):
            try:
                alpha = -float('inf')
                beta = float('inf')
                current_best_move = None
                current_best_score = -float('inf') if maximizing else float('inf')
                
                for move in legal_moves:
                    if time.time() - start_time > time_limit:
                        return best_move if best_move else legal_moves[0]
                    
                    board.push(move)
                    try:
                        score = self.alpha_beta(board, current_depth - 1, alpha, beta, not maximizing, start_time, time_limit)
                    except TimeoutError:
                        board.pop()
                        return best_move if best_move else legal_moves[0]
                    board.pop()
                    
                    if maximizing:
                        if score > current_best_score:
                            current_best_score = score
                            current_best_move = move
                            alpha = max(alpha, score)
                    else:
                        if score < current_best_score:
                            current_best_score = score
                            current_best_move = move
                            beta = min(beta, score)
                    
                    if beta <= alpha:
                        break
                
                if current_best_move:
                    best_move = current_best_move
                    best_score = current_best_score
                
            except TimeoutError:
                break
        
        return best_move if best_move else legal_moves[0]
    
    def reset(self):
        """Reset AI state"""
        super().reset()
