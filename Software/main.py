"""
========================================================
 AIRPEN – Main Application
========================================================
 Real-Time Air Writing Recognition System
 Entry point that orchestrates all modules.

 Usage:
     python main.py

 Press ESC to quit, C to clear recognized text.
========================================================
"""

import cv2
import time
from udp_receiver import UDPReceiver
from signal_processor import SignalProcessor
from motion_tracker import MotionTracker
from drawing_engine import DrawingEngine
from recognizer import Recognizer
from ui_renderer import UIRenderer


def main():
    print("=" * 60)
    print("  AIRPEN – Air Writing Recognition System")
    print("=" * 60)
    print()

    # ── Initialize modules ──
    print("[Main] Initializing modules...")
    receiver = UDPReceiver()
    processor = SignalProcessor()
    tracker = MotionTracker()
    engine = DrawingEngine()
    recognizer = Recognizer()
    ui = UIRenderer()

    print("[Main] All modules ready.")
    print("[Main] Waiting for AirPen data on UDP...\n")

    # ── State ──
    connected = False
    last_write_state = 0

    # ── Main Loop ──
    try:
        while True:
            # ── 1. Receive sensor data (drain buffer for lowest latency) ──
            data = receiver.drain()

            if data is not None:
                if not connected:
                    connected = True
                    ui.set_status("Connected", (0, 255, 0))
                    print("[Main] AirPen connected!")

                # ── 2. Signal processing ──
                dx, dy = processor.process(data.ax, data.ay)

                # ── 3. Update cursor position ──
                tracker.update(dx, dy)
                interp_points = tracker.interpolate_points()

                # ── 4. Update drawing engine ──
                engine.update(
                    cursor_pos=tracker.get_position(),
                    prev_pos=tracker.get_prev_position(),
                    write_state=data.write_state,
                    erase_state=data.erase_state,
                    interp_points=interp_points,
                )

                # ── 5. Track activity for auto-recognition ──
                if data.write_state == 1:
                    recognizer.notify_activity()
                    if last_write_state == 0:
                        ui.set_status("Writing...", (0, 200, 255))
                elif last_write_state == 1:
                    ui.set_status("Idle - recognizing soon...", (255, 200, 0))

                last_write_state = data.write_state

            # ── 6. Check auto-recognition ──
            result = recognizer.check_and_recognize(
                canvas=engine.get_clean_canvas(),
                has_strokes=engine.has_strokes(),
                is_drawing=engine.is_actively_drawing(),
            )
            if result:
                ui.add_char(result)
                ui.set_status(f"Recognized: {result}", (0, 255, 120))
                engine.clear()
                tracker.reset()
                processor.reset()

            # ── 7. Render UI ──
            canvas_frame = engine.get_display_frame(tracker.get_position())
            frame = ui.render(canvas_frame)

            cv2.imshow("AirPen - Air Writing Recognition", frame)

            # ── 8. Handle keyboard ──
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord("c") or key == ord("C"):
                ui.clear_text()
                engine.clear()
                tracker.reset()
                processor.reset()
                ui.set_status("Cleared", (255, 255, 0))

    except KeyboardInterrupt:
        print("\n[Main] Interrupted by user")
    finally:
        receiver.close()
        cv2.destroyAllWindows()
        print("[Main] AirPen shutdown complete.")


if __name__ == "__main__":
    main()
