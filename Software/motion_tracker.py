"""
========================================================
 AIRPEN – Motion Tracking Module
========================================================
 Converts filtered sensor deltas into stable cursor
 coordinates with boundary clamping and interpolation.
========================================================
"""

import math
from config import CANVAS_W, CANVAS_H


class MotionTracker:
    """Manages cursor position on the drawing canvas."""

    def __init__(self):
        # Start at canvas center
        self.cx = CANVAS_W / 2
        self.cy = CANVAS_H / 2
        self._prev_cx = self.cx
        self._prev_cy = self.cy

    def update(self, dx: float, dy: float):
        """
        Move cursor by (dx, dy) pixels, clamped to canvas bounds.

        Note: ax maps to horizontal (X), ay maps to vertical (Y).
        The sign may need adjustment depending on AirPen orientation.
        Currently: positive ax → move right, positive ay → move down.
        """
        self._prev_cx = self.cx
        self._prev_cy = self.cy

        # Apply movement — ay controls X (tilt left/right), ax controls Y (tilt forward/back)
        self.cx += dy   # Lateral tilt → horizontal cursor
        self.cy += dx   # Forward tilt → vertical cursor

        # Clamp to canvas boundaries
        self.cx = max(0, min(CANVAS_W - 1, self.cx))
        self.cy = max(0, min(CANVAS_H - 1, self.cy))

    def get_position(self) -> tuple[int, int]:
        """Return current cursor position as integer pixel coords."""
        return int(self.cx), int(self.cy)

    def get_prev_position(self) -> tuple[int, int]:
        """Return previous cursor position for line interpolation."""
        return int(self._prev_cx), int(self._prev_cy)

    def interpolate_points(self, steps: int = 0) -> list[tuple[int, int]]:
        """
        Generate interpolated points between previous and current position.
        Used for smooth line drawing without gaps.

        Args:
            steps: Number of intermediate points (0 = auto based on distance)

        Returns:
            List of (x, y) points from previous to current position
        """
        x0, y0 = self.get_prev_position()
        x1, y1 = self.get_position()

        dist = math.hypot(x1 - x0, y1 - y0)
        if dist < 1:
            return [(x1, y1)]

        if steps <= 0:
            steps = max(int(dist), 2)

        points = []
        for i in range(steps + 1):
            t = i / steps
            x = int(x0 + (x1 - x0) * t)
            y = int(y0 + (y1 - y0) * t)
            points.append((x, y))

        return points

    def reset(self):
        """Reset cursor to canvas center."""
        self.cx = CANVAS_W / 2
        self.cy = CANVAS_H / 2
        self._prev_cx = self.cx
        self._prev_cy = self.cy
