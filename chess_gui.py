"""
Chess graphical interface
Implemented using pygame
"""
import pygame
import chess
from chess import square_name
from typing import Dict, Optional, Tuple

from ui_components import Theme, Button


AI_ELO_RATINGS = {
    "random": 1426,
    "greedy": 1421,
    "minimax": {2: 1554, 3: 1580, 4: 1600},  
    "alphabeta": {3: 1572, 4: 1590, 5: 1610},
    "negamax": {3: 1553, 4: 1580, 5: 1600},
    "advanced": {5: 1600, 7: 1650},  
}

def get_ai_elo_from_name(ai_name: str) -> Optional[int]:
    
    if not ai_name or ai_name == "Player":
        return None
    
    ai_name_lower = ai_name.lower()
    
    depth = None
    if "depth" in ai_name_lower:
        try:
            import re
            match = re.search(r'depth\s*(\d+)', ai_name_lower)
            if match:
                depth = int(match.group(1))
        except (ValueError, AttributeError):
            pass
    
    ai_type = None
    if "random" in ai_name_lower:
        ai_type = "random"
    elif "greedy" in ai_name_lower:
        ai_type = "greedy"
    elif "minimax" in ai_name_lower:
        ai_type = "minimax"
    elif "alpha" in ai_name_lower or "alphabeta" in ai_name_lower:
        ai_type = "alphabeta"
    elif "negamax" in ai_name_lower:
        ai_type = "negamax"
    elif "advanced" in ai_name_lower:
        ai_type = "advanced"
    
    if ai_type and ai_type in AI_ELO_RATINGS:
        rating = AI_ELO_RATINGS[ai_type]
        if isinstance(rating, dict):

            if depth is None:
                depth = 3 
            available_depths = sorted(rating.keys())
            closest_depth = min(available_depths, key=lambda d: abs(d - depth))
            return rating[closest_depth]
        else:
            return rating
    
    return None


MOVE_DOT_COLOR = (60, 180, 75, 180)
CAPTURE_HIGHLIGHT_COLOR = (236, 80, 80, 180)
SELECTED_SQUARE_COLOR = (255, 206, 92)
LAST_MOVE_COLOR = (120, 170, 255)
LEGAL_HIGHLIGHT_COLOR = (245, 230, 120)

PIECE_SYMBOLS = {
    "K": "♔",
    "Q": "♕",
    "R": "♖",
    "B": "♗",
    "N": "♘",
    "P": "♙",
    "k": "♚",
    "q": "♛",
    "r": "♜",
    "b": "♝",
    "n": "♞",
    "p": "♟",
}


class ChessGUI:
    """Chess graphical interface"""

    MIN_WIDTH = 720
    MIN_HEIGHT = 600

    def __init__(self, width: int = 960, height: int = 720):
        if not pygame.get_init():
            pygame.init()

        self.theme = Theme()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Chess AI")

        self.window_width = width
        self.window_height = height

        self.square_size = 0
        self.board_size = 0
        self.board_origin_x = 0
        self.board_origin_y = 0
        self.top_bar_height = 0
        self.info_panel_height = 0

        self.font = self._load_symbol_font(48)
        self.small_font = Theme.get_font(18)
        self.info_font = Theme.get_font(28, bold=True)
        self.label_font = Theme.get_font(20)

        self.selected_square: Optional[int] = None
        self.valid_moves: list[chess.Move] = []
        self.valid_targets: Dict[int, chess.Move] = {}
        self.last_move: Optional[chess.Move] = None

        self.control_buttons: list[Button] = []
        self.save_button_enabled = False

        self._update_layout(width, height)

    def _load_symbol_font(self, size: int) -> pygame.font.Font:
        """Load fonts that support chess symbols"""
        preferred_fonts = [
            "Segoe UI Symbol",
            "DejaVu Sans",
            "Arial Unicode MS",
            "Noto Sans Symbols",
            "Symbola",
        ]
        for font_name in preferred_fonts:
            try:
                font = pygame.font.SysFont(font_name, size)
                test_surface = font.render(PIECE_SYMBOLS["k"], True, (0, 0, 0))
                if test_surface.get_width() > 0:
                    return font
            except Exception:
                continue
        return pygame.font.Font(None, size)

    def _init_controls(self) -> None:
        button_width = max(160, int(self.window_width * 0.18))
        button_height = max(40, int(self.top_bar_height * 0.55))
        spacing = max(12, int(self.window_width * 0.015))
        x = max(18, int(self.window_width * 0.04))
        y = self.top_bar_height / 2 - button_height / 2

        self.control_buttons = [
            Button(
                (x, y, button_width, button_height),
                "Back to Menu",
                self.theme,
                action="back",
                variant="secondary",
            ),
            Button(
                (x + (button_width + spacing), y, button_width, button_height),
                "Restart",
                self.theme,
                action="restart",
                variant="secondary",
            ),
            Button(
                (x + 2 * (button_width + spacing), y, button_width, button_height),
                "Save Score",
                self.theme,
                action="save",
                variant="primary",
            ),
        ]
        self.set_save_enabled(self.save_button_enabled)


    def clear_selection(self) -> None:
        self.selected_square = None
        self.valid_moves = []
        self.valid_targets = {}

    def set_save_enabled(self, enabled: bool) -> None:
        self.save_button_enabled = enabled
        for button in self.control_buttons:
            if button.action == "save":
                button.set_disabled(not enabled)


    def draw_top_bar(self, game_mode: str, move_count: int, current_player: str) -> None:
        top_rect = pygame.Rect(0, 0, self.window_width, self.top_bar_height)
        pygame.draw.rect(self.screen, self.theme.top_bar, top_rect)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.control_buttons:
            button.update_hover(mouse_pos)
            button.draw(self.screen)

        if game_mode.startswith("H2M"):
            mode_label = "H2M"
        elif game_mode.startswith("M2M"):
            mode_label = "M2M"
        else:
            mode_label = game_mode
        info_font = Theme.get_font(max(18, int(self.top_bar_height * 0.34)))
        info_text = f"Mode: {mode_label}  |  Moves: {move_count}  |  Turn: {current_player}"
        info_surface = info_font.render(info_text, True, self.theme.text_primary)
        info_rect = info_surface.get_rect()
        info_rect.midright = (self.window_width - 24, self.top_bar_height / 2)
        self.screen.blit(info_surface, info_rect)

    def draw_board(self, board: chess.Board) -> None:
        move_map = {move.to_square: move for move in self.valid_moves}
        board_x = self.board_origin_x
        board_y = self.board_origin_y

        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                base_color = (
                    self.theme.board_light if (row + col) % 2 == 0 else self.theme.board_dark
                )
                rect = pygame.Rect(
                    board_x + col * self.square_size,
                    board_y + row * self.square_size,
                    self.square_size,
                    self.square_size,
                )

                color = base_color
                if self.last_move and (
                    square == self.last_move.from_square or square == self.last_move.to_square
                ):
                    color = LAST_MOVE_COLOR
                if self.selected_square == square:
                    color = SELECTED_SQUARE_COLOR
                elif square in move_map:
                    color = LEGAL_HIGHLIGHT_COLOR

                pygame.draw.rect(self.screen, color, rect)

                move = move_map.get(square)
                if move:
                    overlay = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                    center = (self.square_size // 2, self.square_size // 2)
                    if board.is_capture(move):
                        pygame.draw.circle(
                            overlay,
                            CAPTURE_HIGHLIGHT_COLOR,
                            center,
                            self.square_size // 2 - 6,
                            width=6,
                        )
                    else:
                        pygame.draw.circle(
                            overlay,
                            MOVE_DOT_COLOR,
                            center,
                            self.square_size // 6,
                        )
                    self.screen.blit(
                        overlay,
                        (rect.x, rect.y),
                    )

                piece = board.piece_at(square)
                if piece:
                    piece_symbol = PIECE_SYMBOLS.get(piece.symbol(), piece.symbol())
                    text_color = (235, 235, 235) if piece.color == chess.WHITE else (20, 20, 20)
                    outline_color = (30, 30, 30) if piece.color == chess.WHITE else (220, 220, 220)
                    outline_width = max(1, int(self.square_size * 0.02))  
                    
                    outline_offsets = [
                        (-outline_width, -outline_width),  
                        (-outline_width, 0),              
                        (-outline_width, outline_width),  
                        (0, -outline_width),              
                        (0, outline_width),               
                        (outline_width, -outline_width),  
                        (outline_width, 0),               
                        (outline_width, outline_width),   
                    ]
                    
                    for offset_x, offset_y in outline_offsets:
                        outline_surface = self.font.render(piece_symbol, True, outline_color)
                        outline_rect = outline_surface.get_rect(center=rect.center)
                        outline_rect.x += offset_x
                        outline_rect.y += offset_y
                        self.screen.blit(outline_surface, outline_rect)
                    
                    text_surface = self.font.render(piece_symbol, True, text_color)
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.screen.blit(text_surface, text_rect)

        files = "abcdefgh"
        ranks = "12345678"
        for i in range(8):
            file_surface = self.small_font.render(files[i], True, self.theme.text_muted)
            file_rect = file_surface.get_rect()
            file_rect.bottomleft = (
                board_x + i * self.square_size + 6,
                board_y + self.board_size - 6,
            )
            self.screen.blit(file_surface, file_rect)

            rank_surface = self.small_font.render(ranks[7 - i], True, self.theme.text_muted)
            rank_rect = rank_surface.get_rect()
            rank_rect.topleft = (board_x + 6, board_y + i * self.square_size + 6)
            self.screen.blit(rank_surface, rank_rect)

    def draw_info_panel(
        self,
        board: chess.Board,
        current_player: str,
        game_mode: str,
        white_ai: str,
        black_ai: str,
        move_count: int,
    ) -> None:
        panel_rect = pygame.Rect(
            0,
            self.window_height - self.info_panel_height,
            self.window_width,
            self.info_panel_height,
        )
        pygame.draw.rect(self.screen, self.theme.panel_bg, panel_rect)

        pygame.draw.line(
            self.screen,
            (45, 50, 68),
            (0, panel_rect.top),
            (self.window_width, panel_rect.top),
            2,
        )

        text_x = max(20, int(self.window_width * 0.03))
        text_y = panel_rect.top + 16
        line_spacing = 8  
        info_font = Theme.get_font(max(22, int(self.info_panel_height * 0.32)), bold=True)

        current_text = info_font.render(
            f"Current Player: {current_player}", True, self.theme.text_primary
        )
        self.screen.blit(current_text, (text_x, text_y))
        text_y += current_text.get_height() + line_spacing

        mode_text = self.label_font.render(f"Mode: {game_mode}", True, self.theme.text_muted)
        self.screen.blit(mode_text, (text_x, text_y))
        text_y += mode_text.get_height() + line_spacing

        if white_ai or black_ai:
            white_elo = get_ai_elo_from_name(white_ai) if white_ai else None
            black_elo = get_ai_elo_from_name(black_ai) if black_ai else None
            
            white_display = white_ai or "Player"
            if white_elo:
                white_display = f"{white_ai} (Elo: {white_elo})"
            
            black_display = black_ai or "Player"
            if black_elo:
                black_display = f"{black_ai} (Elo: {black_elo})"
            
            ai_text = self.label_font.render(
                f"White: {white_display}  |  Black: {black_display}",
                True,
                self.theme.text_muted,
            )

            max_width = self.window_width - text_x - 200  
            if ai_text.get_width() > max_width:

                white_short = white_ai.split()[0] if white_ai else "Player"
                black_short = black_ai.split()[0] if black_ai else "Player"
                if white_elo:
                    white_short = f"{white_short} (Elo: {white_elo})"
                if black_elo:
                    black_short = f"{black_short} (Elo: {black_elo})"
                ai_text = self.label_font.render(
                    f"W: {white_short} | B: {black_short}",
                    True,
                    self.theme.text_muted,
                )
            self.screen.blit(ai_text, (text_x, text_y))
            text_y += ai_text.get_height() + line_spacing

        moves_text = self.label_font.render(
            f"Moves: {move_count}", True, self.theme.text_muted
        )
        self.screen.blit(moves_text, (text_x, text_y))
        text_y += moves_text.get_height() + line_spacing

        if self.selected_square is not None:
            selected = square_name(self.selected_square)
            selected_text = self.label_font.render(f"Selected: {selected}", True, self.theme.text_muted)
            if text_y + selected_text.get_height() < panel_rect.bottom - 10:
                self.screen.blit(selected_text, (text_x, text_y))

        status = None
        if board.is_checkmate():
            status = "Checkmate! White Wins" if board.turn == chess.BLACK else "Checkmate! Black Wins"
        elif board.is_stalemate():
            status = "Stalemate!"
        elif board.is_check():
            status = "Check!"

        if status:
            status_surface = Theme.get_font(30, bold=True).render(
                status, True, self.theme.accent_primary
            )
            status_rect = status_surface.get_rect()
            status_rect.midright = (self.window_width - 24, panel_rect.top + 40)
            self.screen.blit(status_surface, status_rect)


    def get_square_from_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        x, y = pos
        if x < self.board_origin_x or x >= self.board_origin_x + self.board_size:
            return None
        if y < self.board_origin_y or y >= self.board_origin_y + self.board_size:
            return None
        col = (x - self.board_origin_x) // self.square_size
        row = 7 - ((y - self.board_origin_y) // self.square_size)
        return chess.square(col, row)

    def handle_click(self, pos: Tuple[int, int], board: chess.Board) -> Optional[chess.Move]:
        square = self.get_square_from_pos(pos)
        if square is None:
            self.clear_selection()
            return None

        if self.selected_square is None:
            piece = board.piece_at(square)
            if piece and piece.color == board.turn:
                self.selected_square = square
                self.valid_moves = [
                    move for move in board.legal_moves if move.from_square == square
                ]
        else:
            move = next((m for m in self.valid_moves if m.to_square == square), None)
            if move:
                self.clear_selection()
                return move
            piece = board.piece_at(square)
            if piece and piece.color == board.turn:
                self.selected_square = square
                self.valid_moves = [
                    move for move in board.legal_moves if move.from_square == square
                ]
            else:
                self.clear_selection()

        self.valid_targets = {move.to_square: move for move in self.valid_moves}
        return None

    def handle_event(self, event: pygame.event.Event, board: chess.Board):

        if event.type == pygame.MOUSEMOTION:
            for button in self.control_buttons:
                button.update_hover(event.pos)
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.control_buttons:
                action = button.handle_event(event)
                if action:
                    return ("action", action)
            move = self.handle_click(event.pos, board)
            if move:
                return ("move", move)

        return None


    def update(
        self,
        board: chess.Board,
        current_player: str,
        game_mode: str,
        white_ai: str,
        black_ai: str,
        move_count: int,
        last_move: Optional[chess.Move] = None,
    ) -> None:
        self.screen.fill(self.theme.background)
        self.last_move = last_move
        self.draw_top_bar(game_mode, move_count, current_player)
        self.draw_board(board)
        self.draw_info_panel(board, current_player, game_mode, white_ai, black_ai, move_count)
        pygame.display.flip()


    def show_message(self, message: str) -> bool:
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        text = Theme.get_font(42, bold=True).render(message, True, self.theme.text_primary)
        text_rect = text.get_rect(center=(self.window_width // 2, self.window_height // 2))
        panel = pygame.Surface((text_rect.width + 80, text_rect.height + 60), pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            self.theme.panel_bg,
            panel.get_rect(),
            border_radius=self.theme.border_radius,
        )
        panel.blit(text, text.get_rect(center=panel.get_rect().center))
        panel_rect = panel.get_rect(center=(self.window_width // 2, self.window_height // 2))
        self.screen.blit(panel, panel_rect)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    waiting = False
        return True

    def close(self) -> None:
        pass


    def _update_layout(self, width: int, height: int) -> None:
        self.window_width = max(self.MIN_WIDTH, width)
        self.window_height = max(self.MIN_HEIGHT, height)

        self.top_bar_height = 65
        self.info_panel_height = 120  

        margin = 20
        available_height = self.window_height - self.top_bar_height - self.info_panel_height - margin * 2
        available_width = self.window_width - margin * 2
        
        board_size = min(available_width, available_height)
        board_size = max(400, board_size)  
        board_size = min(board_size, available_width, available_height)
        board_size = (board_size // 8) * 8
        
        self.square_size = board_size // 8
        self.board_size = self.square_size * 8

        self.board_origin_x = (self.window_width - self.board_size) // 2
        available_vertical_space = self.window_height - self.top_bar_height - self.info_panel_height
        self.board_origin_y = self.top_bar_height + max(10, (available_vertical_space - self.board_size) // 2)
        
        min_board_y = self.top_bar_height + 10
        max_board_y = self.window_height - self.info_panel_height - self.board_size - 10
        self.board_origin_y = max(min_board_y, min(self.board_origin_y, max_board_y))

        self.font = self._load_symbol_font(int(self.square_size * 0.85))
        self.small_font = Theme.get_font(max(14, int(self.square_size * 0.22)))
        self.info_font = Theme.get_font(max(24, int(self.info_panel_height * 0.35)), bold=True)
        self.label_font = Theme.get_font(max(18, int(self.info_panel_height * 0.24)))

        self._init_controls()

