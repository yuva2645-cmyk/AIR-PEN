"""
========================================================
 AIRPEN – Signal Processing Module
========================================================
 Stabilizes noisy MPU6050 acceleration data through:
   1. Exponential Moving Average (low-pass filter)
   2. Dead-zone filtering (tremor removal)
   3. Motion scaling with speed clamping
========================================================
"""

from config import ALPHA, DEAD_ZONE, MOVE_SCALE, MAX_SPEED


class SignalProcessor:
    """Three-stage signal processing pipeline for IMU data."""

    def __init__(self):
        # EMA filter state
        self._filtered_ax = 0.0
        self._filtered_ay = 0.0

    def process(self, raw_ax: float, raw_ay: float) -> tuple[float, float]:
        """
        Process raw accelerometer values through the full pipeline.

        Args:
            raw_ax: Raw X-axis acceleration from sensor
            raw_ay: Raw Y-axis acceleration from sensor

        Returns:
            (dx, dy): Smoothed pixel displacement for cursor movement
        """
        # Stage 1: Exponential Moving Average (low-pass filter)
        self._filtered_ax = ALPHA * raw_ax + (1 - ALPHA) * self._filtered_ax
        self._filtered_ay = ALPHA * raw_ay + (1 - ALPHA) * self._filtered_ay

        # Stage 2: Dead-zone filtering (remove small tremors)
        ax = self._filtered_ax if abs(self._filtered_ax) >= DEAD_ZONE else 0.0
        ay = self._filtered_ay if abs(self._filtered_ay) >= DEAD_ZONE else 0.0

        # Stage 3: Scale to pixel displacement and clamp speed
        dx = self._clamp(ax * MOVE_SCALE, MAX_SPEED)
        dy = self._clamp(ay * MOVE_SCALE, MAX_SPEED)

        return dx, dy

    def reset(self):
        """Reset filter state (e.g., after recognition)."""
        self._filtered_ax = 0.0
        self._filtered_ay = 0.0

    @staticmethod
    def _clamp(value: float, limit: float) -> float:
        """Clamp value to [-limit, +limit]."""
        if value > limit:
            return limit
        if value < -limit:
            return -limit
        return value
