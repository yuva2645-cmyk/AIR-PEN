"""
========================================================
 AIRPEN – UI Renderer Module
========================================================
 Dual-panel layout: live canvas (left) + info panel (right)
 Renders recognized text, status, and instructions.
========================================================
"""

import numpy as np
import cv2
from config import (
    CANVAS_W, CANVAS_H, PANEL_WIDTH,
    PANEL_BG_COLOR, PANEL_TEXT_COLOR,
    PANEL_ACCENT_COLOR, PANEL_TITLE_COLOR,
)


class UIRenderer:
    """Dual-panel UI for AirPen application."""

    def __init__(self):
        self.recognized_chars: list[str] = []
        self.status = "Waiting for AirPen..."
        self.status_color = PANEL_TEXT_COLOR

    def add_char(self, char: str):
        """Add a recognized character to the output."""
        self.recognized_chars.append(char)

    def set_status(self, text: str, color: tuple = None):
        """Update status message."""
        self.status = text
        self.status_color = color if color else PANEL_TEXT_COLOR

    def get_recognized_text(self) -> str:
        """Get full recognized text string."""
        return "".join(self.recognized_chars)

    def clear_text(self):
        """Clear recognized text."""
        self.recognized_chars.clear()

    def render(self, canvas_frame: np.ndarray) -> np.ndarray:
        """
        Compose the full UI frame.

        Args:
            canvas_frame: Left panel canvas (with cursor overlay)

        Returns:
            Combined frame (canvas + info panel)
        """
        panel = self._render_panel()
        combined = np.hstack([canvas_frame, panel])
        return combined

    def _render_panel(self) -> np.ndarray:
        """Render the right information panel."""
        panel = np.zeros((CANVAS_H, PANEL_WIDTH, 3), dtype=np.uint8)
        panel[:] = PANEL_BG_COLOR

        # ── Decorative top accent line ──
        cv2.line(panel, (0, 0), (PANEL_WIDTH, 0),
                 PANEL_ACCENT_COLOR, 3)

        # ── Title ──
        y = 45
        cv2.putText(panel, "AIRPEN", (20, y),
                     cv2.FONT_HERSHEY_SIMPLEX, 1.1,
                     PANEL_TITLE_COLOR, 2, cv2.LINE_AA)

        # ── Subtitle ──
        y += 30
        cv2.putText(panel, "Air Writing System", (20, y),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                     (120, 120, 140), 1, cv2.LINE_AA)

        # ── Divider ──
        y += 20
        cv2.line(panel, (20, y), (PANEL_WIDTH - 20, y),
                 (50, 50, 60), 1)

        # ── Status ──
        y += 35
        cv2.putText(panel, "STATUS", (20, y),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                     (100, 100, 120), 1, cv2.LINE_AA)
        y += 25
        # Status indicator dot
        cv2.circle(panel, (30, y - 5), 5, self.status_color, -1, cv2.LINE_AA)
        cv2.putText(panel, self.status, (45, y),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                     self.status_color, 1, cv2.LINE_AA)

        # ── Divider ──
        y += 25
        cv2.line(panel, (20, y), (PANEL_WIDTH - 20, y),
                 (50, 50, 60), 1)

        # ── Recognized Text Section ──
        y += 35
        cv2.putText(panel, "RECOGNIZED TEXT", (20, y),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                     (100, 100, 120), 1, cv2.LINE_AA)

        y += 15

        # Text display area background
        text_area_y = y
        cv2.rectangle(panel,
                       (15, text_area_y),
                       (PANEL_WIDTH - 15, text_area_y + 120),
                       (30, 30, 45), -1)
        cv2.rectangle(panel,
                       (15, text_area_y),
                       (PANEL_WIDTH - 15, text_area_y + 120),
                       (60, 60, 80), 1)

        # Render recognized characters
        text = self.get_recognized_text()
        if text:
            # Wrap text into lines
            max_chars = 12
            lines = [text[i:i + max_chars]
                     for i in range(0, len(text), max_chars)]
            ty = text_area_y + 35
            for line in lines[:4]:  # Max 4 lines
                cv2.putText(panel, line, (25, ty),
                             cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                             PANEL_ACCENT_COLOR, 2, cv2.LINE_AA)
                ty += 28
        else:
            cv2.putText(panel, "Write to start...", (25, text_area_y + 45),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                         (80, 80, 100), 1, cv2.LINE_AA)

        y = text_area_y + 135

        # ── Divider ──
        cv2.line(panel, (20, y), (PANEL_WIDTH - 20, y),
                 (50, 50, 60), 1)

        # ── Last Character (large display) ──
        y += 35
        cv2.putText(panel, "LAST CHARACTER", (20, y),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                     (100, 100, 120), 1, cv2.LINE_AA)
        y += 10

        if self.recognized_chars:
            last_char = self.recognized_chars[-1]
            # Large character display box
            box_x, box_y = 20, y
            box_size = 80
            cv2.rectangle(panel,
                           (box_x, box_y),
                           (box_x + box_size, box_y + box_size),
                           (30, 30, 45), -1)
            cv2.rectangle(panel,
                           (box_x, box_y),
                           (box_x + box_size, box_y + box_size),
                           PANEL_ACCENT_COLOR, 2)
            # Center the character
            cv2.putText(panel, last_char,
                         (box_x + 15, box_y + 60),
                         cv2.FONT_HERSHEY_SIMPLEX, 2.0,
                         (255, 255, 255), 3, cv2.LINE_AA)

        y += 100

        # ── Divider ──
        cv2.line(panel, (20, y), (PANEL_WIDTH - 20, y),
                 (50, 50, 60), 1)

        # ── Controls ──
        y += 30
        cv2.putText(panel, "CONTROLS", (20, y),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                     (100, 100, 120), 1, cv2.LINE_AA)

        controls = [
            ("Write Btn", "Draw strokes"),
            ("Erase Btn", "Undo last stroke"),
            ("ESC", "Quit application"),
            ("C key", "Clear all text"),
        ]
        y += 10
        for label, desc in controls:
            y += 22
            cv2.putText(panel, label, (25, y),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                         PANEL_ACCENT_COLOR, 1, cv2.LINE_AA)
            cv2.putText(panel, f"  {desc}", (110, y),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                         (140, 140, 160), 1, cv2.LINE_AA)

        return panel
