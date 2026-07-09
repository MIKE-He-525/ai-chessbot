"""
Main program entry
Chess AI project
"""
import sys
from datetime import datetime
import pygame

from game_controller import GameController
from ui_components import Theme, Button


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 720


AI_ELO_RATINGS = {
    "random": 1426,
    "greedy": 1421,
    "minimax": {2: 1554, 3: 1580, 4: 1600},  
    "alphabeta": {3: 1572, 4: 1590, 5: 1610},
    "negamax": {3: 1553, 4: 1580, 5: 1600},
    "advanced": {5: 1600, 7: 1650},  
}

def get_ai_elo(ai_type: str, depth: int = None) -> int:
    """Get the Elo rating of AI"""
    if ai_type not in AI_ELO_RATINGS:
        return 1400  
    
    rating = AI_ELO_RATINGS[ai_type]
    if isinstance(rating, dict):
        if depth is None:
            depth = 3  
        available_depths = sorted(rating.keys())
        closest_depth = min(available_depths, key=lambda d: abs(d - depth))
        return rating[closest_depth]
    else:
        return rating


class MainMenu:
    """Main menu interface"""

    def __init__(self):
        pygame.init()
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess AI - Main Menu")
        self.clock = pygame.time.Clock()
        self.theme = Theme()

        self.controller = GameController()
        self.state = "main"
        self.buttons: list[Button] = []

        self._update_fonts()

        self.ai_options = ["random", "greedy", "minimax", "alphabeta", "negamax", "advanced"]
        self.h2m_player_color = True
        self.h2m_ai_index = 2
        self.h2m_difficulty = 3

        self.m2m_white_index = 2
        self.m2m_black_index = 3
        self.m2m_white_diff = 3
        self.m2m_black_diff = 4
        self.m2m_delay_options = [0.2, 0.5, 1.0, 1.5, 2.0]
        self.m2m_delay_index = 2
        self.m2m_move_limits = [100, 150, 200, 300, 500]
        self.m2m_move_index = 2

        self.cached_scores: list[dict] = []

        self._set_state("main")


    def _set_state(self, state: str) -> None:
        self.state = state
        self._update_fonts()
        if state == "main":
            self._create_main_buttons()
        elif state == "h2m":
            self._create_h2m_buttons()
        elif state == "m2m":
            self._create_m2m_buttons()
        elif state == "scores":
            self._create_scores_buttons()
        elif state == "ai_intro":
            self._create_ai_intro_buttons()

    def _update_fonts(self) -> None:
        self.title_font = Theme.get_font(52, bold=True)
        self.subtitle_font = Theme.get_font(24)
        self.body_font = Theme.get_font(20)
        self.small_body_font = Theme.get_font(18)


 

    def _create_main_buttons(self) -> None:
        button_width = 300
        button_height = 56
        spacing = 16
        start_y = 220
        x = self.width // 2 - button_width // 2
        
        self.buttons = [
            Button((x, start_y, button_width, button_height), "Human vs AI", self.theme, action="goto_h2m"),
            Button(
                (x, start_y + (button_height + spacing), button_width, button_height),
                "AI vs AI Battle",
                self.theme,
                action="goto_m2m",
            ),
            Button(
                (x, start_y + 2 * (button_height + spacing), button_width, button_height),
                "Bot Introduction",
                self.theme,
                action="goto_ai_intro",
            ),
            Button(
                (x, start_y + 3 * (button_height + spacing), button_width, button_height),
                "Score Records",
                self.theme,
                action="goto_scores",
            ),
            Button(
                (x, start_y + 4 * (button_height + spacing), button_width, button_height),
                "Exit",
                self.theme,
                action="exit",
                variant="danger",
            ),
        ]

    def _create_h2m_buttons(self) -> None:
        panel_width = 440
        button_width = 360
        button_height = 52
        spacing = 14
        panel_x = self.width // 2 - panel_width // 2
        
        start_y = 210
        total_height = 5 * button_height + 4 * spacing
        panel_padding = 30  
        panel_height = total_height + panel_padding * 2
        
        button_x = panel_x + (panel_width - button_width) // 2
        button_start_y = start_y + panel_padding  

        self.h2m_color_button = Button(
            (button_x, button_start_y, button_width, button_height),
            "",
            self.theme,
            action="toggle_color",
            variant="secondary",
        )
        self.h2m_ai_button = Button(
            (button_x, button_start_y + (button_height + spacing), button_width, button_height),
            "",
            self.theme,
            action="cycle_ai",
            variant="secondary",
        )
        self.h2m_diff_button = Button(
            (button_x, button_start_y + 2 * (button_height + spacing), button_width, button_height),
            "",
            self.theme,
            action="difficulty_up",
            variant="secondary",
        )
        self.h2m_start_button = Button(
            (button_x, button_start_y + 3 * (button_height + spacing), button_width, button_height),
            "Start Game",
            self.theme,
            action="start_h2m",
            variant="primary",
        )
        self.h2m_back_button = Button(
            (button_x, button_start_y + 4 * (button_height + spacing), button_width, button_height),
            "Back to Main",
            self.theme,
            action="back_main",
            variant="secondary",
        )

        self.buttons = [
            self.h2m_color_button,
            self.h2m_ai_button,
            self.h2m_diff_button,
            self.h2m_start_button,
            self.h2m_back_button,
        ]
        self._update_h2m_labels()

        self._h2m_panel_rect = pygame.Rect(
            self.width // 2 - panel_width // 2,
            start_y,  
            panel_width,
            panel_height,  
        )

    def _create_m2m_buttons(self) -> None:
        
        panel_width = 500
        button_width = 400
        button_height = 44  
        spacing = 10  
        panel_x = self.width // 2 - panel_width // 2
        
        start_y = 200
        total_height = 8 * button_height + 7 * spacing
        panel_padding = 25  
        panel_height = total_height + panel_padding * 2
        
        button_x = panel_x + (panel_width - button_width) // 2
        button_start_y = start_y + panel_padding  

        self.m2m_white_ai_button = Button(
            (button_x, button_start_y, button_width, button_height),
            "",
            self.theme,
            action="cycle_white_ai",
            variant="secondary",
        )
        self.m2m_white_diff_button = Button(
            (button_x, button_start_y + (button_height + spacing), button_width, button_height),
            "",
            self.theme,
            action="white_diff",
            variant="secondary",
        )
        self.m2m_black_ai_button = Button(
            (button_x, button_start_y + 2 * (button_height + spacing), button_width, button_height),
            "",
            self.theme,
            action="cycle_black_ai",
            variant="secondary",
        )
        self.m2m_black_diff_button = Button(
            (button_x, button_start_y + 3 * (button_height + spacing), button_width, button_height),
            "",
            self.theme,
            action="black_diff",
            variant="secondary",
        )
        self.m2m_delay_button = Button(
            (button_x, button_start_y + 4 * (button_height + spacing), button_width, button_height),
            "",
            self.theme,
            action="toggle_delay",
            variant="secondary",
        )
        self.m2m_max_moves_button = Button(
            (button_x, button_start_y + 5 * (button_height + spacing), button_width, button_height),
            "",
            self.theme,
            action="toggle_max_moves",
            variant="secondary",
        )
        self.m2m_start_button = Button(
            (button_x, button_start_y + 6 * (button_height + spacing), button_width, button_height),
            "Start Battle",
            self.theme,
            action="start_m2m",
            variant="primary",
        )
        self.m2m_back_button = Button(
            (button_x, button_start_y + 7 * (button_height + spacing), button_width, button_height),
            "Back to Main",
            self.theme,
            action="back_main",
            variant="secondary",
        )

        self.buttons = [
            self.m2m_white_ai_button,
            self.m2m_white_diff_button,
            self.m2m_black_ai_button,
            self.m2m_black_diff_button,
            self.m2m_delay_button,
            self.m2m_max_moves_button,
            self.m2m_start_button,
            self.m2m_back_button,
        ]
        self._update_m2m_labels()

        self._m2m_panel_rect = pygame.Rect(
            self.width // 2 - panel_width // 2,
            start_y,  
            panel_width,
            panel_height,  
        )

    def _create_scores_buttons(self) -> None:
        self.cached_scores = self.controller.score_manager.get_scores()
        button_width = 220
        button_height = 50
        center_x = self.width // 2
        bottom_margin = 50
        button_y = self.height - bottom_margin - button_height
        
        self.buttons = [
            Button(
                (center_x - button_width - 15, button_y, button_width, button_height),
                "Clear Records",
                self.theme,
                action="clear_scores",
                variant="danger",
            ),
            Button(
                (center_x + 15, button_y, button_width, button_height),
                "Back to Main",
                self.theme,
                action="back_main",
                variant="secondary",
            ),
        ]
        margin_x = 80
        top = 180  
        bottom_margin = 20  
        height = button_y - top - bottom_margin  
        height = max(200, height)  
        self._scores_panel_rect = pygame.Rect(
            margin_x,
            top,
            self.width - 2 * margin_x,
            height,
        )

    def _create_ai_intro_buttons(self) -> None:
        """Create buttons for the AI introduction interface"""
        button_width = 220
        button_height = 50
        center_x = self.width // 2
        bottom_margin = 50
        button_y = self.height - bottom_margin - button_height
        
        self.buttons = [
            Button(
                (center_x - button_width // 2, button_y, button_width, button_height),
                "Back to Main",
                self.theme,
                action="back_main",
                variant="secondary",
            ),
        ]
        
        margin_x = 60
        top = 180
        bottom_margin = 20
        height = button_y - top - bottom_margin
        height = max(300, height)
        self._ai_intro_panel_rect = pygame.Rect(
            margin_x,
            top,
            self.width - 2 * margin_x,
            height,
        )


    def _update_h2m_labels(self) -> None:
        color = "White" if self.h2m_player_color else "Black"
        self.h2m_color_button.set_text(f"Player Color: {color}")
        ai_name = self.ai_options[self.h2m_ai_index].title()
        ai_type = self.ai_options[self.h2m_ai_index]
        elo = get_ai_elo(ai_type, self.h2m_difficulty)
        self.h2m_ai_button.set_text(f"AI Type: {ai_name} (Elo: {elo})")
        self.h2m_diff_button.set_text(f"AI Difficulty: {self.h2m_difficulty}")

    def _update_m2m_labels(self) -> None:
        white_ai_name = self.ai_options[self.m2m_white_index].title()
        black_ai_name = self.ai_options[self.m2m_black_index].title()
        white_ai_type = self.ai_options[self.m2m_white_index]
        black_ai_type = self.ai_options[self.m2m_black_index]
        white_elo = get_ai_elo(white_ai_type, self.m2m_white_diff)
        black_elo = get_ai_elo(black_ai_type, self.m2m_black_diff)
        self.m2m_white_ai_button.set_text(f"White AI: {white_ai_name} (Elo: {white_elo})")
        self.m2m_white_diff_button.set_text(f"White AI Strength: {self.m2m_white_diff}")
        self.m2m_black_ai_button.set_text(f"Black AI: {black_ai_name} (Elo: {black_elo})")
        self.m2m_black_diff_button.set_text(f"Black AI Strength: {self.m2m_black_diff}")
        delay_value = self.m2m_delay_options[self.m2m_delay_index]
        self.m2m_delay_button.set_text(f"Move Delay: {delay_value:.1f} s (click to change)")
        max_moves = self.m2m_move_limits[self.m2m_move_index]
        self.m2m_max_moves_button.set_text(f"Max Moves: {max_moves}")


    def _draw_panel(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, self.theme.panel_bg, rect, border_radius=self.theme.border_radius)

    def draw_main(self) -> None:
        self.screen.fill(self.theme.background)
        title_y = 80
        subtitle_y = 130

        title = self.title_font.render("Chess AI Bot", True, self.theme.text_primary)
        self.screen.blit(title, title.get_rect(center=(self.width // 2, title_y)))

        subtitle = self.subtitle_font.render(
            "Explore intelligent chess battles across multiple AI levels",
            True,
            self.theme.text_muted,
        )
        self.screen.blit(subtitle, subtitle.get_rect(center=(self.width // 2, subtitle_y)))

        for button in self.buttons:
            button.draw(self.screen)

        footer = self.body_font.render(
            "Tip: Use the in-game top bar to restart, save scores, or return to the menu.",
            True,
            self.theme.text_muted,
        )
        self.screen.blit(footer, footer.get_rect(center=(self.width // 2, self.height - 40)))

    def draw_h2m(self) -> None:
        self.screen.fill(self.theme.background)
        title_y = 80
        desc_y = 130

        title = self.title_font.render("Human vs AI Settings", True, self.theme.text_primary)
        self.screen.blit(title, title.get_rect(center=(self.width // 2, title_y)))

        desc = self.body_font.render(
            "Configure your opponent before starting the match.", True, self.theme.text_muted
        )
        self.screen.blit(desc, desc.get_rect(center=(self.width // 2, desc_y)))

        panel_rect = getattr(self, "_h2m_panel_rect", pygame.Rect(self.width // 2 - 230, 190, 460, 360))
        self._draw_panel(panel_rect)

        for button in self.buttons:
            button.draw(self.screen)

    def draw_m2m(self) -> None:
        self.screen.fill(self.theme.background)
        title_y = 80
        desc_y = 130

        title = self.title_font.render("AI vs AI Battle Settings", True, self.theme.text_primary)
        self.screen.blit(title, title.get_rect(center=(self.width // 2, title_y)))

        desc = self.body_font.render(
            "Pit two AI opponents against each other and watch the chess fireworks.",
            True,
            self.theme.text_muted,
        )
        self.screen.blit(desc, desc.get_rect(center=(self.width // 2, desc_y)))

        self._draw_panel(self._m2m_panel_rect)

        for button in self.buttons:
            button.draw(self.screen)

    def draw_scores(self) -> None:
        self.screen.fill(self.theme.background)
        title = self.title_font.render("Score Records", True, self.theme.text_primary)
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 120)))

        panel_rect = getattr(self, "_scores_panel_rect", pygame.Rect(140, 180, self.width - 280, self.height - 360))
        self._draw_panel(panel_rect)

        if not self.cached_scores:
            placeholder = self.body_font.render(
                "No records yet. Play a match and save the result!", True, self.theme.text_muted
            )
            self.screen.blit(placeholder, placeholder.get_rect(center=panel_rect.center))
        else:
            line_y = panel_rect.top + 20
            line_height = 64
            max_entries = (panel_rect.height - 40) // line_height
            text_margin = 24
            max_text_width = panel_rect.width - text_margin * 2  
            
            for record in self.cached_scores[:max_entries]:
                if line_y + line_height > panel_rect.bottom - 20:
                    break
                    
                timestamp = self._format_timestamp(record.get("timestamp", ""))
                mode = record.get("mode", "")
                if mode == "H2M":
                    summary = (
                        f"{timestamp}  |  Human ({record.get('player_color')}) "
                        f"{record.get('human_outcome')} vs {record.get('ai_name', '')}"
                    )
                    result_label = (record.get("result") or "").title()
                    detail = (
                        f"Score: {record.get('score')}  • Moves: {record.get('moves')}  "
                        f"• Difficulty: {record.get('difficulty')}  • Result: {result_label}"
                    )
                else:
                    summary = (
                        f"{timestamp}  |  {record.get('white_ai')} vs {record.get('black_ai')}  "
                        f"→ {record.get('winner')}"
                    )
                    delay_value = record.get("move_delay")
                    if isinstance(delay_value, (int, float)):
                        delay_text = f"{delay_value:.1f}"
                    else:
                        delay_text = "-"
                    result_label = (record.get("result") or "").title()
                    detail = (
                        f"Moves: {record.get('moves')}  • Delay: {delay_text}s  "
                        f"• Result: {result_label}"
                    )

                summary_surface = self.body_font.render(summary, True, self.theme.text_primary)
                if summary_surface.get_width() > max_text_width:
                    while summary_surface.get_width() > max_text_width and len(summary) > 0:
                        summary = summary[:-1]
                        summary_surface = self.body_font.render(summary + "...", True, self.theme.text_primary)
                
                detail_surface = self.small_body_font.render(detail, True, self.theme.text_muted)
                if detail_surface.get_width() > max_text_width:
                    while detail_surface.get_width() > max_text_width and len(detail) > 0:
                        detail = detail[:-1]
                        detail_surface = self.small_body_font.render(detail + "...", True, self.theme.text_muted)
                
                self.screen.blit(summary_surface, (panel_rect.left + text_margin, line_y))
                self.screen.blit(detail_surface, (panel_rect.left + text_margin, line_y + 28))
                line_y += line_height

        for button in self.buttons:
            button.draw(self.screen)

    def draw_ai_intro(self) -> None:
        """Draw an AI introduction interface"""
        self.screen.fill(self.theme.background)
        title = self.title_font.render("AI Introduction", True, self.theme.text_primary)
        self.screen.blit(title, title.get_rect(center=(self.width // 2, 120)))

        panel_rect = getattr(self, "_ai_intro_panel_rect", pygame.Rect(60, 180, self.width - 120, self.height - 360))
        self._draw_panel(panel_rect)

        ai_introductions = [
            {
                "name": "Advanced AI",
                "ai_type": "advanced",
                "depth": 7,  
                "elo": "~1650+",
                "rank": "1",
                "description": "Master-level AI with dual-mode design.",
                "features": "Iterative deepening, Quiescence search, Enhanced evaluation, Transposition table, Dual-mode optimization"
            },
            {
                "name": "Alpha-Beta AI",
                "ai_type": "alphabeta",
                "depth": 3,
                "elo": "~1572",
                "rank": "2",
                "description": "Classic game search with Alpha-Beta pruning. Strong performance.",
                "features": "Pruning, Move ordering, Optimized evaluation"
            },
            {
                "name": "Minimax AI",
                "ai_type": "minimax",
                "depth": 2,
                "elo": "~1554",
                "rank": "3",
                "description": "Full-width game tree search with transposition table.",
                "features": "Alpha-Beta, TT cache, Move prioritization"
            },
            {
                "name": "Negamax AI",
                "ai_type": "negamax",
                "depth": 3,
                "elo": "~1553",
                "rank": "4",
                "description": "Symmetric Minimax variant with cleaner implementation.",
                "features": "Alpha-Beta, Consistent evaluation, Elegant code"
            },
            {
                "name": "Random AI",
                "ai_type": "random",
                "depth": 0,
                "elo": "~1426",
                "rank": "5",
                "description": "Random legal moves. Baseline for testing.",
                "features": "No strategy, Fast, Beginner level"
            },
            {
                "name": "Greedy AI",
                "ai_type": "greedy",
                "depth": 0,
                "elo": "~1421",
                "rank": "6",
                "description": "One-ply lookahead. Captures immediate material gains.",
                "features": "Single-step, Material-focused, Short-sighted"
            },
        ]
        
        for ai_info in ai_introductions:
            if "ai_type" in ai_info and "depth" in ai_info:
                elo = get_ai_elo(ai_info["ai_type"], ai_info["depth"])
                if isinstance(elo, int):
                    if ai_info["ai_type"] == "advanced" and ai_info["depth"] == 7:
                        ai_info["elo"] = "~1650+"
                    else:
                        ai_info["elo"] = f"~{elo}"

        text_x = panel_rect.left + 24
        text_y = panel_rect.top + 20
        line_spacing = 4
        entry_spacing = 12
        
        title_font = Theme.get_font(22, bold=True)
        body_font = Theme.get_font(18)
        small_font = Theme.get_font(16)

        for ai_info in ai_introductions:
            if text_y + 80 > panel_rect.bottom - 20:
                break

            rank_name = f"#{ai_info['rank']} {ai_info['name']} (Elo: {ai_info['elo']})"
            rank_surface = title_font.render(rank_name, True, self.theme.accent_primary)
            self.screen.blit(rank_surface, (text_x, text_y))
            text_y += rank_surface.get_height() + line_spacing

            desc_surface = body_font.render(ai_info['description'], True, self.theme.text_primary)
            self.screen.blit(desc_surface, (text_x, text_y))
            text_y += desc_surface.get_height() + line_spacing

            features_text = f"Features: {ai_info['features']}"
            features_surface = small_font.render(features_text, True, self.theme.text_muted)
            self.screen.blit(features_surface, (text_x, text_y))
            text_y += features_surface.get_height() + entry_spacing

        for button in self.buttons:
            button.draw(self.screen)

    def _format_timestamp(self, timestamp: str) -> str:
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            return timestamp


    def _handle_action(self, action: str) -> None:
        if action == "goto_h2m":
            self._set_state("h2m")
        elif action == "goto_m2m":
            self._set_state("m2m")
        elif action == "goto_scores":
            self._set_state("scores")
        elif action == "goto_ai_intro":
            self._set_state("ai_intro")
        elif action == "back_main":
            self._set_state("main")
        elif action == "exit":
            pygame.quit()
            sys.exit()
        elif action == "toggle_color":
            self.h2m_player_color = not self.h2m_player_color
            self._update_h2m_labels()
        elif action == "cycle_ai":
            self.h2m_ai_index = (self.h2m_ai_index + 1) % len(self.ai_options)
            self._update_h2m_labels()
        elif action == "difficulty_up":
            self.h2m_difficulty = (self.h2m_difficulty % 5) + 1
            self._update_h2m_labels()
        elif action == "start_h2m":
            self._start_h2m_game()
        elif action == "cycle_white_ai":
            self.m2m_white_index = (self.m2m_white_index + 1) % len(self.ai_options)
            self._update_m2m_labels()
        elif action == "cycle_black_ai":
            self.m2m_black_index = (self.m2m_black_index + 1) % len(self.ai_options)
            self._update_m2m_labels()
        elif action == "white_diff":
            self.m2m_white_diff = (self.m2m_white_diff % 5) + 1
            self._update_m2m_labels()
        elif action == "black_diff":
            self.m2m_black_diff = (self.m2m_black_diff % 5) + 1
            self._update_m2m_labels()
        elif action == "toggle_delay":
            self.m2m_delay_index = (self.m2m_delay_index + 1) % len(self.m2m_delay_options)
            self._update_m2m_labels()
        elif action == "toggle_max_moves":
            self.m2m_move_index = (self.m2m_move_index + 1) % len(self.m2m_move_limits)
            self._update_m2m_labels()
        elif action == "start_m2m":
            self._start_m2m_game()
        elif action == "clear_scores":
            self.controller.score_manager.clear()
            self._create_scores_buttons()

    def _start_h2m_game(self) -> None:
        ai_type = self.ai_options[self.h2m_ai_index]
        self.controller.h2m_game(
            player_color=self.h2m_player_color,
            ai_type=ai_type,
            difficulty=self.h2m_difficulty,
            window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            fullscreen=False,
        )
        self._set_state("main")

    def _start_m2m_game(self) -> None:
        white_ai = self.ai_options[self.m2m_white_index]
        black_ai = self.ai_options[self.m2m_black_index]
        move_delay = self.m2m_delay_options[self.m2m_delay_index]
        max_moves = self.m2m_move_limits[self.m2m_move_index]
        self.controller.m2m_game(
            white_ai_type=white_ai,
            black_ai_type=black_ai,
            white_difficulty=self.m2m_white_diff,
            black_difficulty=self.m2m_black_diff,
            move_delay=move_delay,
            max_moves=max_moves,
            window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            fullscreen=False,
        )
        self._set_state("main")

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.state != "main":
                    self._set_state("main")
                    continue
            if event.type == pygame.MOUSEMOTION:
                for button in self.buttons:
                    button.update_hover(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.buttons:
                    action = button.handle_event(event)
                    if action:
                        self._handle_action(action)
                        break


    def run(self) -> None:
        while True:
            if self.state == "main":
                self.draw_main()
            elif self.state == "h2m":
                self.draw_h2m()
            elif self.state == "m2m":
                self.draw_m2m()
            elif self.state == "scores":
                self.draw_scores()
            elif self.state == "ai_intro":
                self.draw_ai_intro()

            pygame.display.flip()
            self.handle_events()
            self.clock.tick(60)


def main():
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()

