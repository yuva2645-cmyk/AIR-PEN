"""
========================================================
 AIRPEN – UDP Test Simulator
========================================================
 Simulates an ESP32 AirPen device by sending test
 UDP packets. Use this to test the app without hardware.

 Usage:
     python test_udp_sender.py

 Controls:
     W = Start writing (hold)
     E = Erase last stroke
     Arrow keys = Move (simulated acceleration)
     Q = Quit
========================================================
"""

import socket
import time
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 5005


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("AirPen UDP Simulator")
    print("Sending test packets to", UDP_IP, UDP_PORT)
    print()
    print("Sending a test pattern (circle)...")

    import math

    # Draw a circle pattern
    write_state = 1
    erase_state = 0
    radius = 2000
    steps = 200

    for i in range(steps):
        angle = 2 * math.pi * i / steps
        ax = int(radius * math.cos(angle))
        ay = int(radius * math.sin(angle))

        packet = f"{ax},{ay},{write_state},{erase_state}"
        sock.sendto(packet.encode(), (UDP_IP, UDP_PORT))
        time.sleep(0.015)

    # Stop writing
    for _ in range(20):
        sock.sendto(b"0,0,0,0", (UDP_IP, UDP_PORT))
        time.sleep(0.015)

    print("Circle pattern sent!")
    print("Waiting for recognition (1 second)...")
    time.sleep(2)

    # Draw letter L pattern
    print("Drawing 'L' pattern...")
    write_state = 1

    # Vertical stroke down
    for i in range(80):
        packet = f"2000,0,{write_state},{erase_state}"
        sock.sendto(packet.encode(), (UDP_IP, UDP_PORT))
        time.sleep(0.015)

    # Horizontal stroke right
    for i in range(50):
        packet = f"0,2000,{write_state},{erase_state}"
        sock.sendto(packet.encode(), (UDP_IP, UDP_PORT))
        time.sleep(0.015)

    # Stop
    for _ in range(100):
        sock.sendto(b"0,0,0,0", (UDP_IP, UDP_PORT))
        time.sleep(0.015)

    print("Test complete!")
    sock.close()


if __name__ == "__main__":
    main()
