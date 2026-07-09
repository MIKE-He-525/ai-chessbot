"""
Game Controller
Manages H2M and M2M game modes
"""
import chess
import time
import pygame
from datetime import datetime
from typing import Optional, Tuple
from chess_engine import ChessEngine
from ai_players import AIPlayer, RandomAI, GreedyAI, MinimaxAI, AlphaBetaAI, NegamaxAI, AdvancedAI
from chess_gui import ChessGUI
from score_manager import ScoreManager

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720

class GameController:
    """game controller"""
    
    def __init__(self):
        self.engine = ChessEngine()
        self.gui: Optional[ChessGUI] = None
        self.move_count = 0
        self.game_history = []
        self.score_manager = ScoreManager()
        
    def create_ai(self, ai_type: str, color: bool, difficulty: int = 3) -> AIPlayer:
        """Create an AI player"""
        ai_map = {
            "random": RandomAI,
            "greedy": GreedyAI,
            "minimax": lambda c: MinimaxAI(c, difficulty),
            "alphabeta": lambda c: AlphaBetaAI(c, difficulty),
            "negamax": lambda c: NegamaxAI(c, difficulty),
            "advanced": lambda c: AdvancedAI(c, max(5, difficulty + 4), test_mode=False)
        }
        
        if ai_type not in ai_map:
            ai_type = "random"
        
        return ai_map[ai_type](color)
    
    def h2m_game(
        self,
        player_color: bool = True,
        ai_type: str = "minimax",
        difficulty: int = 3,
        window_size: Optional[Tuple[int, int]] = None,
        fullscreen: bool = False,
    ):
        """人机对战模式"""
        width, height = window_size if window_size else (960, 720)
        self.gui = ChessGUI(width, height)
        self.gui.set_save_enabled(False)
        self.gui.clear_selection()

        self.engine.reset()
        self.move_count = 0
        self.game_history = []

        ai = self.create_ai(ai_type, not player_color, difficulty)

        running = True
        clock = pygame.time.Clock()
        ai_thinking = False
        game_finished = False
        score_saved = False

        while running:
            current_turn = self.engine.get_turn()
            current_player = "White" if current_turn else "Black"

            last_move = self.game_history[-1] if self.game_history else None
            self.gui.update(
                self.engine.board,
                current_player,
                "H2M (Human vs AI)",
                "",
                ai.name,
                self.move_count,
                last_move,
            )

            if self.engine.is_game_over() and not game_finished:
                result = self.engine.get_result()
                if result == "white":
                    message = "White Wins!"
                elif result == "black":
                    message = "Black Wins!"
                else:
                    message = "Draw!"
                self.gui.set_save_enabled(True)
                self.gui.show_message(message)
                game_finished = True
                self.gui.clear_selection()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                result_event = self.gui.handle_event(event, self.engine.board)
                if result_event:
                    kind, payload = result_event
                    if kind == "layout":
                        continue
                    if kind == "move" and not game_finished and current_turn == player_color and not ai_thinking:
                        move = payload
                        if move:
                            if self.engine.make_move(move):
                                self.game_history.append(move)
                                self.move_count += 1
                        continue
                    if kind == "action":
                        if payload == "back":
                            running = False
                            break
                        if payload == "restart":
                            self.engine.reset()
                            self.move_count = 0
                            self.game_history = []
                            self.gui.clear_selection()
                            self.gui.set_save_enabled(False)
                            game_finished = False
                            score_saved = False
                            continue
                        if payload == "save" and game_finished and not score_saved:
                            self._record_h2m_score(
                                player_color,
                                ai_type,
                                ai.name,
                                difficulty,
                                self.engine.get_result(),
                            )
                            score_saved = True
                            self.gui.set_save_enabled(False)
                            continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    if (
                        event.key == pygame.K_u
                        and self.game_history
                        and current_turn == player_color
                        and not game_finished
                    ):
                        self.engine.undo_move()
                        self.game_history.pop()
                        self.move_count = max(0, self.move_count - 1)
                        self.gui.clear_selection()

            if not running:
                break

            if current_turn != player_color and not ai_thinking and not game_finished:
                ai_thinking = True
                pygame.event.pump()
                time.sleep(0.3)
                ai_move = ai.get_move(self.engine.board)
                if ai_move:
                    self.engine.make_move(ai_move)
                    self.game_history.append(ai_move)
                    self.move_count += 1
                ai_thinking = False
                self.gui.clear_selection()

            clock.tick(60)

        self.gui = None
    
    def m2m_game(
        self,
        white_ai_type: str = "minimax",
        black_ai_type: str = "minimax",
        white_difficulty: int = 3,
        black_difficulty: int = 3,
        move_delay: float = 1.0,
        max_moves: int = 200,
        window_size: Optional[Tuple[int, int]] = None,
        fullscreen: bool = False,
    ):
        """M2M"""
        width, height = window_size if window_size else (960, 720)
        self.gui = ChessGUI(width, height)
        self.gui.set_save_enabled(False)
        self.gui.clear_selection()
        
        self.engine.reset()
        self.move_count = 0
        self.game_history = []
        
        white_ai = self.create_ai(white_ai_type, True, white_difficulty)
        black_ai = self.create_ai(black_ai_type, False, black_difficulty)
        
        running = True
        clock = pygame.time.Clock()
        game_finished = False
        score_saved = False
        position_history = []  
        
        while running and self.move_count < max_moves:
            current_turn = self.engine.get_turn()
            current_player = "White" if current_turn else "Black"
            current_ai = white_ai if current_turn else black_ai
            
            # Update interface
            last_move = self.game_history[-1] if self.game_history else None
            self.gui.update(
                self.engine.board,
                current_player,
                "M2M (Machine vs Machine)",
                white_ai.name,
                black_ai.name,
                self.move_count,
                last_move
            )
            
            
            if not game_finished:
                
                if self.engine.is_game_over():
                    result = self.engine.get_result()
                    if result == "white":
                        message = f"White ({white_ai.name}) Wins!"
                    elif result == "black":
                        message = f"Black ({black_ai.name}) Wins!"
                    else:
                        message = "Draw!"
                    self.gui.set_save_enabled(True)
                    self.gui.show_message(message)
                    game_finished = True
                    self.gui.clear_selection()
                
                elif self.engine.board.is_repetition(3):
                    message = "Draw by repetition!"
                    self.gui.set_save_enabled(True)
                    self.gui.show_message(message)
                    game_finished = True
                    self.gui.clear_selection()
                
                elif self.engine.board.is_fifty_moves():
                    message = "Draw by 50-move rule!"
                    self.gui.set_save_enabled(True)
                    self.gui.show_message(message)
                    game_finished = True
                    self.gui.clear_selection()
                
                elif self.engine.board.is_insufficient_material():
                    message = "Draw by insufficient material!"
                    self.gui.set_save_enabled(True)
                    self.gui.show_message(message)
                    game_finished = True
                    self.gui.clear_selection()
                
                elif not list(self.engine.board.legal_moves):
                    message = "Draw by stalemate!"
                    self.gui.set_save_enabled(True)
                    self.gui.show_message(message)
                    game_finished = True
                    self.gui.clear_selection()
            
            if not game_finished:
                
                legal_moves = list(self.engine.board.legal_moves)
                if not legal_moves:
                    
                    message = "No legal moves. Game over."
                    self.gui.set_save_enabled(True)
                    self.gui.show_message(message)
                    game_finished = True
                    self.gui.clear_selection()
                else:
                    
                    ai_move = current_ai.get_move(self.engine.board)
                    if ai_move and ai_move in legal_moves:
                        
                        current_fen = self.engine.board.fen()
                        position_history.append(current_fen)
                        
                        
                        self.engine.make_move(ai_move)
                        self.game_history.append(ai_move)
                        self.move_count += 1
                        
                        
                        new_fen = self.engine.board.fen()
                        if position_history.count(new_fen) >= 2:  
                            message = "Draw by repetition!"
                            self.gui.set_save_enabled(True)
                            self.gui.show_message(message)
                            game_finished = True
                            self.gui.clear_selection()
                    else:
                        
                        if legal_moves:
                            ai_move = legal_moves[0]
                            current_fen = self.engine.board.fen()
                            position_history.append(current_fen)
                            self.engine.make_move(ai_move)
                            self.game_history.append(ai_move)
                            self.move_count += 1
                        else:
                            
                            message = "No valid moves. Game over."
                            self.gui.set_save_enabled(True)
                            self.gui.show_message(message)
                            game_finished = True
                            self.gui.clear_selection()
                self.gui.clear_selection()

            if not game_finished:
                time.sleep(move_delay)
            else:
                time.sleep(0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                result_event = self.gui.handle_event(event, self.engine.board)
                if result_event:
                    kind, payload = result_event
                    if kind == "layout":
                        continue
                    if kind == "action":
                        if payload == "back":
                            running = False
                            break
                        if payload == "restart":
                            self.engine.reset()
                            self.move_count = 0
                            self.game_history = []
                            self.gui.clear_selection()
                            self.gui.set_save_enabled(False)
                            game_finished = False
                            score_saved = False
                            continue
                        if payload == "save" and game_finished and not score_saved:
                            self._record_m2m_score(
                                white_ai_type,
                                white_ai.name,
                                white_difficulty,
                                black_ai_type,
                                black_ai.name,
                                black_difficulty,
                                self.engine.get_result(),
                                move_delay,
                            )
                            score_saved = True
                            self.gui.set_save_enabled(False)
                            continue
            if not running:
                break
            
            clock.tick(60)
        
        
        final_result = None
        if self.move_count >= max_moves and not game_finished:
            
            if self.engine.is_game_over():
                final_result = self.engine.get_result()
            elif self.engine.board.is_repetition(3):
                final_result = "draw"
            elif self.engine.board.is_fifty_moves():
                final_result = "draw"
            elif self.engine.board.is_insufficient_material():
                final_result = "draw"
            else:
                final_result = "draw" 
            
            message = f"Maximum moves ({max_moves}) reached. Result: {final_result}."
            self.gui.show_message(message)
            game_finished = True
            time.sleep(2)
        
        
        if game_finished:
            if final_result is None:
                final_result = self.engine.get_result()
            if final_result is None:
                
                if self.engine.board.is_repetition(3):
                    final_result = "draw"
                elif self.engine.board.is_fifty_moves():
                    final_result = "draw"
                elif self.engine.board.is_insufficient_material():
                    final_result = "draw"
                else:
                    final_result = "draw"  
        
        result_data = {
            "result": final_result if game_finished else self.engine.get_result(),
            "moves": self.move_count,
            "history": self.game_history
        }
        self.gui = None
        return result_data

    def _record_h2m_score(
        self,
        player_color: bool,
        ai_label: str,
        ai_display_name: str,
        difficulty: int,
        result: Optional[str],
    ) -> None:
        if result is None:
            return
        human_side = "white" if player_color else "black"
        if result == "draw":
            outcome = "Draw"
        elif result == human_side:
            outcome = "Win"
        else:
            outcome = "Loss"

        base = 120 + difficulty * 40
        if outcome == "Win":
            score_value = base + max(0, 60 - self.move_count)
        elif outcome == "Draw":
            score_value = base // 2
        else:
            score_value = max(20, base // 3)

        record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "mode": "H2M",
            "player_color": "White" if player_color else "Black",
            "ai_type": ai_label,
            "ai_name": ai_display_name,
            "difficulty": difficulty,
            "result": result,
            "human_outcome": outcome,
            "moves": self.move_count,
            "score": int(score_value),
        }
        self.score_manager.add_record(record)

    def _record_m2m_score(
        self,
        white_ai_label: str,
        white_ai_name: str,
        white_diff: int,
        black_ai_label: str,
        black_ai_name: str,
        black_diff: int,
        result: Optional[str],
        move_delay: float,
    ) -> None:
        if result is None:
            return
        if result == "white":
            winner = f"White ({white_ai_name})"
        elif result == "black":
            winner = f"Black ({black_ai_name})"
        else:
            winner = "Draw"

        record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "mode": "M2M",
            "white_ai": white_ai_name,
            "white_type": white_ai_label,
            "white_difficulty": white_diff,
            "black_ai": black_ai_name,
            "black_type": black_ai_label,
            "black_difficulty": black_diff,
            "result": result,
            "winner": winner,
            "moves": self.move_count,
            "move_delay": move_delay,
            "score": 0,
        }
        self.score_manager.add_record(record)
    

