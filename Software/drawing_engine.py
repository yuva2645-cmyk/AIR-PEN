"""
========================================================
 AIRPEN – Drawing Engine
========================================================
 Manages canvas rendering, stroke storage, and drawing
 with smooth line interpolation.
========================================================
"""

import numpy as np
import cv2
from config import (
    CANVAS_W, CANVAS_H, BG_COLOR, STROKE_COLOR,
    STROKE_THICKNESS, CURSOR_COLOR, CURSOR_RADIUS,
)


class DrawingEngine:
    """Real-time drawing engine with stroke management."""

    def __init__(self):
        # Main canvas (strokes only, no cursor)
        self.canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
        self.canvas[:] = BG_COLOR

        # Stroke storage: list of strokes, each stroke is a list of (x,y)
        self.strokes: list[list[tuple[int, int]]] = []
        self._current_stroke: list[tuple[int, int]] = []
        self._is_drawing = False

        # Erase button state tracking (edge detection)
        self._prev_erase = 0

    def update(self, cursor_pos: tuple[int, int], prev_pos: tuple[int, int],
               write_state: int, erase_state: int,
               interp_points: list[tuple[int, int]] | None = None):
        """
        Update the drawing engine for one frame.

        Args:
            cursor_pos: Current cursor (x, y)
            prev_pos: Previous cursor (x, y)
            write_state: 1 = pen down (drawing), 0 = pen up
            erase_state: 1 = erase button pressed
            interp_points: Optional interpolated points for smooth lines
        """
        # ── Handle erase (edge-triggered: only on press) ──
        if erase_state == 1 and self._prev_erase == 0:
            self._erase_last_stroke()
        self._prev_erase = erase_state

        # ── Handle drawing ──
        if write_state == 1:
            if not self._is_drawing:
                # Start new stroke
                self._is_drawing = True
                self._current_stroke = [cursor_pos]
            else:
                # Continue stroke with interpolated points
                points = interp_points if interp_points else [cursor_pos]
                for pt in points:
                    if self._current_stroke:
                        last = self._current_stroke[-1]
                        cv2.line(self.canvas, last, pt,
                                 STROKE_COLOR, STROKE_THICKNESS,
                                 lineType=cv2.LINE_AA)
                    self._current_stroke.append(pt)
        else:
            if self._is_drawing:
                # Finalize stroke
                if len(self._current_stroke) > 1:
                    self.strokes.append(self._current_stroke.copy())
                self._current_stroke = []
                self._is_drawing = False

    def get_display_frame(self, cursor_pos: tuple[int, int]) -> np.ndarray:
        """
        Return canvas with cursor overlay (for display only).
        The cursor is NOT burned into the stored canvas.
        """
        frame = self.canvas.copy()
        cv2.circle(frame, cursor_pos, CURSOR_RADIUS,
                   CURSOR_COLOR, -1, lineType=cv2.LINE_AA)
        # Draw a subtle outer ring
        cv2.circle(frame, cursor_pos, CURSOR_RADIUS + 2,
                   CURSOR_COLOR, 1, lineType=cv2.LINE_AA)
        return frame

    def get_clean_canvas(self) -> np.ndarray:
        """Return canvas without cursor (for recognition)."""
        return self.canvas.copy()

    def has_strokes(self) -> bool:
        """Check if there are any completed or in-progress strokes."""
        return len(self.strokes) > 0 or len(self._current_stroke) > 1

    def is_actively_drawing(self) -> bool:
        """Check if currently in the middle of a stroke."""
        return self._is_drawing

    def clear(self):
        """Clear all strokes and reset canvas."""
        self.canvas[:] = BG_COLOR
        self.strokes.clear()
        self._current_stroke.clear()
        self._is_drawing = False

    def _erase_last_stroke(self):
        """Remove the last completed stroke and redraw canvas."""
        if not self.strokes:
            return

        self.strokes.pop()
        self._redraw()

    def _redraw(self):
        """Redraw all strokes from scratch onto a clean canvas."""
        self.canvas[:] = BG_COLOR
        for stroke in self.strokes:
            for i in range(1, len(stroke)):
                cv2.line(self.canvas, stroke[i - 1], stroke[i],
                         STROKE_COLOR, STROKE_THICKNESS,
                         lineType=cv2.LINE_AA)
