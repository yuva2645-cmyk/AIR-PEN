"""
========================================================
 AIRPEN – UDP Receiver Module
========================================================
 Receives wireless sensor data from ESP32-C3 via UDP.
 Packet format: ax,ay,writeState,eraseState
 Example: 1200,-850,1,0
========================================================
"""

import socket
from config import UDP_IP, UDP_PORT, BUFFER_SIZE


class SensorData:
    """Parsed sensor data from one UDP packet."""

    __slots__ = ("ax", "ay", "write_state", "erase_state")

    def __init__(self, ax: float, ay: float, write_state: int, erase_state: int):
        self.ax = ax
        self.ay = ay
        self.write_state = write_state
        self.erase_state = erase_state

    def __repr__(self):
        return (
            f"SensorData(ax={self.ax}, ay={self.ay}, "
            f"write={self.write_state}, erase={self.erase_state})"
        )


class UDPReceiver:
    """Non-blocking UDP socket receiver for AirPen data."""

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((UDP_IP, UDP_PORT))
        self.sock.setblocking(False)
        print(f"[UDP] Listening on {UDP_IP}:{UDP_PORT}")

    def receive(self) -> SensorData | None:
        """
        Try to receive and parse one UDP packet.
        Returns SensorData on success, None if no data or parse error.
        """
        try:
            data, _ = self.sock.recvfrom(BUFFER_SIZE)
            return self._parse(data.decode("utf-8", errors="ignore").strip())
        except BlockingIOError:
            # No data available — normal for non-blocking socket
            return None
        except Exception:
            return None

    def drain(self) -> SensorData | None:
        """
        Read all pending packets and return only the latest one.
        Prevents buffer buildup and reduces latency.
        """
        latest = None
        for _ in range(50):  # Drain up to 50 buffered packets
            pkt = self.receive()
            if pkt is None:
                break
            latest = pkt
        return latest

    @staticmethod
    def _parse(raw: str) -> SensorData | None:
        """Parse 'ax,ay,writeState,eraseState' string."""
        try:
            parts = raw.split(",")
            if len(parts) != 4:
                return None
            ax = float(parts[0])
            ay = float(parts[1])
            write_state = int(parts[2])
            erase_state = int(parts[3])
            return SensorData(ax, ay, write_state, erase_state)
        except (ValueError, IndexError):
            return None

    def close(self):
        """Close the UDP socket."""
        self.sock.close()
        print("[UDP] Socket closed")
