"""
========================================================
 AIRPEN – Recognizer Module
========================================================
 Handles auto-detection of writing completion, image
 preprocessing, and CNN inference for character recognition.
========================================================
"""

import time
import os
import numpy as np
import cv2

from config import (
    INACTIVITY_TIMEOUT, IMG_SIZE, MODEL_PATH,
    CONFIDENCE_THRESHOLD, CHAR_MAP, NUM_CLASSES,
)


class Recognizer:
    """Auto-detection + image preprocessing + CNN inference."""

    def __init__(self):
        self._last_activity_time = 0.0
        self._recognition_pending = False
        self._model = None
        self._load_model()

    def _load_model(self):
        """Load the trained CNN model."""
        if not os.path.exists(MODEL_PATH):
            print(f"[Recognizer] WARNING: Model not found at '{MODEL_PATH}'")
            print("[Recognizer] Run 'python train_model.py' to train the model.")
            return

        try:
            import tensorflow as tf
            # Suppress TF info logs
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
            tf.get_logger().setLevel("ERROR")

            self._model = tf.keras.models.load_model(MODEL_PATH)
            print(f"[Recognizer] Model loaded from '{MODEL_PATH}'")
        except Exception as e:
            print(f"[Recognizer] Failed to load model: {e}")
            self._model = None

    def notify_activity(self):
        """Called whenever drawing activity occurs."""
        self._last_activity_time = time.time()
        self._recognition_pending = True

    def check_and_recognize(self, canvas: np.ndarray, has_strokes: bool,
                             is_drawing: bool) -> str | None:
        """
        Check if writing has stopped and trigger recognition.

        Args:
            canvas: Clean canvas image (no cursor)
            has_strokes: Whether strokes exist on canvas
            is_drawing: Whether currently in drawing state

        Returns:
            Recognized character string, or None
        """
        if not has_strokes or is_drawing or not self._recognition_pending:
            return None

        elapsed = time.time() - self._last_activity_time
        if elapsed < INACTIVITY_TIMEOUT:
            return None

        # Inactivity timeout reached — recognize!
        self._recognition_pending = False
        return self._recognize(canvas)

    def _recognize(self, canvas: np.ndarray) -> str | None:
        """
        Preprocess canvas and run CNN inference.

        Returns:
            Recognized character or None on failure
        """
        if self._model is None:
            print("[Recognizer] No model loaded — skipping recognition")
            return None

        # Preprocess
        img = self._preprocess(canvas)
        if img is None:
            return None

        # Inference
        try:
            prediction = self._model.predict(img, verbose=0)
            class_idx = int(np.argmax(prediction[0]))
            confidence = float(prediction[0][class_idx])

            char = CHAR_MAP.get(class_idx, "?")
            print(f"[Recognizer] Predicted: '{char}' "
                  f"(class={class_idx}, conf={confidence:.2f})")

            if confidence < CONFIDENCE_THRESHOLD:
                print(f"[Recognizer] Confidence too low, ignoring")
                return None

            return char
        except Exception as e:
            print(f"[Recognizer] Inference error: {e}")
            return None

    def _preprocess(self, canvas: np.ndarray) -> np.ndarray | None:
        """
        Convert canvas to CNN-ready 28×28 image tensor.

        Steps:
            1. Convert to grayscale
            2. Find bounding box of content
            3. Crop with padding
            4. Resize to 28×28
            5. Normalize to [0, 1]
            6. Reshape for CNN input
        """
        # Grayscale
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)

        # Find content bounding box
        coords = cv2.findNonZero(gray)
        if coords is None:
            return None

        x, y, w, h = cv2.boundingRect(coords)

        # Add padding (15% of largest dimension)
        pad = int(max(w, h) * 0.15)
        x = max(0, x - pad)
        y = max(0, y - pad)
        w = min(gray.shape[1] - x, w + 2 * pad)
        h = min(gray.shape[0] - y, h + 2 * pad)

        # Crop
        cropped = gray[y:y + h, x:x + w]

        # Make square by padding shorter dimension
        size = max(w, h)
        square = np.zeros((size, size), dtype=np.uint8)
        offset_x = (size - w) // 2
        offset_y = (size - h) // 2
        square[offset_y:offset_y + h, offset_x:offset_x + w] = cropped

        # Resize to 28×28
        resized = cv2.resize(square, (IMG_SIZE, IMG_SIZE),
                             interpolation=cv2.INTER_AREA)

        # Normalize to [0, 1]
        normalized = resized.astype(np.float32) / 255.0

        # Reshape for CNN: (1, 28, 28, 1)
        tensor = normalized.reshape(1, IMG_SIZE, IMG_SIZE, 1)

        return tensor
