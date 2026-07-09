"""
General UI Components: Themes and Buttons
"""
import pygame
from dataclasses import dataclass
from typing import Callable, Optional, Tuple


def _lighten(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    return tuple(min(255, int(component + (255 - component) * factor)) for component in color)


@dataclass
class Theme:

    background: Tuple[int, int, int] = (25, 28, 38)
    board_light: Tuple[int, int, int] = (210, 220, 245)
    board_dark: Tuple[int, int, int] = (78, 102, 140)
    top_bar: Tuple[int, int, int] = (32, 38, 55)
    panel_bg: Tuple[int, int, int] = (28, 32, 45)
    accent_primary: Tuple[int, int, int] = (88, 133, 251)
    accent_secondary: Tuple[int, int, int] = (98, 104, 128)
    accent_danger: Tuple[int, int, int] = (226, 80, 95)
    button_disabled: Tuple[int, int, int] = (74, 78, 92)
    text_primary: Tuple[int, int, int] = (236, 240, 245)
    text_muted: Tuple[int, int, int] = (165, 172, 185)
    border_radius: int = 14
    shadow_color: Tuple[int, int, int] = (0, 0, 0)
    shadow_alpha: int = 110
    shadow_offset: Tuple[int, int] = (0, 5)

    _font_cache = {}

    preferred_fonts = [
        "Segoe UI",
        "Montserrat",
        "Roboto",
        "Open Sans",
        "Arial Rounded MT Bold",
    ]

    @classmethod
    def get_font(cls, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key in cls._font_cache:
            return cls._font_cache[key]
        for name in cls.preferred_fonts:
            try:
                font = pygame.font.SysFont(name, size, bold=bold)
                surface = font.render("A", True, (255, 255, 255))
                if surface.get_width() > 0:
                    cls._font_cache[key] = font
                    return font
            except Exception:
                continue
        font = pygame.font.Font(None, size)
        cls._font_cache[key] = font
        return font


class Button:

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        text: str,
        theme: Theme,
        *,
        action: Optional[str] = None,
        on_click: Optional[Callable[[], None]] = None,
        variant: str = "primary",
        font: Optional[pygame.font.Font] = None,
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.theme = theme
        self.action = action
        self.on_click = on_click
        self.variant = variant
        self.font = font or Theme.get_font(22, bold=(variant == "primary"))
        self.hover = False
        self.disabled = False

    def set_disabled(self, disabled: bool) -> None:
        self.disabled = disabled

    def set_text(self, text: str) -> None:
        self.text = text

    def update_hover(self, mouse_pos: Tuple[int, int]) -> None:
        if mouse_pos is None:
            self.hover = False
            return
        self.hover = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        base_color, text_color = self._resolve_colors()
        draw_color = base_color
        if self.disabled:
            draw_color = self.theme.button_disabled
            text_color = self.theme.text_muted
        elif self.hover:
            draw_color = _lighten(base_color, 0.15)

        if not self.disabled:
            shadow_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            shadow_rect = shadow_surface.get_rect()
            pygame.draw.rect(
                shadow_surface,
                (*self.theme.shadow_color, self.theme.shadow_alpha),
                shadow_rect,
                border_radius=self.theme.border_radius,
            )
            surface.blit(
                shadow_surface,
                (
                    self.rect.x + self.theme.shadow_offset[0],
                    self.rect.y + self.theme.shadow_offset[1],
                ),
            )

        pygame.draw.rect(
            surface,
            draw_color,
            self.rect,
            border_radius=self.theme.border_radius,
        )

        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if self.disabled:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return self.action
        return None

    def _resolve_colors(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        if self.variant == "secondary":
            return self.theme.accent_secondary, self.theme.text_primary
        if self.variant == "danger":
            return self.theme.accent_danger, self.theme.text_primary
        return self.theme.accent_primary, self.theme.text_primary

