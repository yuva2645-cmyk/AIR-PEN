"""
========================================================
 AIRPEN – Configuration
========================================================
 Central configuration for all tunable parameters.
 Adjust these values to fine-tune the AirPen system.
========================================================
"""

# ──────────────────────────────────────────────────────
#  NETWORK
# ──────────────────────────────────────────────────────
UDP_IP = "0.0.0.0"          # Listen on all interfaces
UDP_PORT = 5005             # Must match ESP32 target port
BUFFER_SIZE = 1024          # UDP receive buffer size (bytes)

# ──────────────────────────────────────────────────────
#  CANVAS
# ──────────────────────────────────────────────────────
CANVAS_W = 800              # Drawing canvas width (px)
CANVAS_H = 600              # Drawing canvas height (px)
BG_COLOR = (0, 0, 0)        # Black background
STROKE_COLOR = (255, 255, 255)  # White drawing strokes
STROKE_THICKNESS = 3        # Stroke line thickness (px)
CURSOR_COLOR = (0, 255, 0)  # Green cursor
CURSOR_RADIUS = 6           # Cursor circle radius (px)

# ──────────────────────────────────────────────────────
#  SIGNAL PROCESSING
# ──────────────────────────────────────────────────────
ALPHA = 0.15                # EMA low-pass filter coefficient (0-1)
                            # Lower = smoother but more lag
DEAD_ZONE = 300             # Ignore acceleration below this value
MOVE_SCALE = 0.04           # Acceleration → pixel displacement scale
MAX_SPEED = 8               # Maximum cursor movement per frame (px)

# ──────────────────────────────────────────────────────
#  RECOGNITION
# ──────────────────────────────────────────────────────
INACTIVITY_TIMEOUT = 1.0    # Seconds of inactivity before auto-recognize
IMG_SIZE = 28               # CNN input image size (28×28)
MODEL_PATH = "models/airpen_cnn.h5"     # Trained model file path
CONFIDENCE_THRESHOLD = 0.4  # Minimum confidence to accept prediction

# ──────────────────────────────────────────────────────
#  UI
# ──────────────────────────────────────────────────────
PANEL_WIDTH = 300           # Right info panel width (px)
PANEL_BG_COLOR = (20, 20, 30)       # Dark panel background
PANEL_TEXT_COLOR = (220, 220, 220)   # Light text
PANEL_ACCENT_COLOR = (0, 200, 120)  # Green accent
PANEL_TITLE_COLOR = (0, 180, 255)   # Blue title

# ──────────────────────────────────────────────────────
#  CHARACTER MAP
# ──────────────────────────────────────────────────────
# MNIST Digits: classes 0-9
CHAR_MAP = {i: str(i) for i in range(10)}

NUM_CLASSES = 10            # 10 digits
