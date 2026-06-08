import cv2
import numpy as np
from traffic.signal_controller import SignalState
import time


SIGNAL_COLORS = {
    SignalState.GREEN:  (0, 220, 0),
    SignalState.YELLOW: (0, 220, 220),
    SignalState.RED:    (0, 0, 220),
}

CONGESTION_COLORS = {
    "LOW":    (0, 200, 0),
    "MEDIUM": (0, 180, 220),
    "HIGH":   (0, 0, 220),
}


class DisplayManager:
    def __init__(self):
        self.lane_w = 320
        self.lane_h = 240
        self.panel_w = 320
        self.header_h = 50
        self.status_h = 110
        self.start_time = time.time()

    def _draw_signal_light(self, canvas, cx, cy, state):
        for s, color_off, y_offset in [
            (SignalState.RED,    (40, 0, 0),   -28),
            (SignalState.YELLOW, (40, 40, 0),    0),
            (SignalState.GREEN,  (0, 40, 0),    28),
        ]:
            color = SIGNAL_COLORS[s] if state == s else color_off
            cv2.circle(canvas, (cx, cy + y_offset), 10, color, -1)
            cv2.circle(canvas, (cx, cy + y_offset), 10, (80, 80, 80), 1)

    def _draw_lane_panel(self, frame, signal_state, time_remaining,
                         vehicle_count, lane_id, congestion):
        panel = frame.copy()
        h, w = panel.shape[:2]

        border_color = SIGNAL_COLORS[signal_state]
        cv2.rectangle(panel, (0, 0), (w - 1, h - 1), border_color, 3)

        overlay = panel.copy()
        cv2.rectangle(overlay, (0, 0), (w, 28), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.7, panel, 0.3, 0, panel)

        cv2.putText(panel, f"Lane {lane_id + 1}", (8, 19),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cong_color = CONGESTION_COLORS[congestion]
        cv2.putText(panel, congestion, (w - 70, 19),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, cong_color, 1)

        self._draw_signal_light(panel, w - 20, h - 50, signal_state)

        cv2.putText(panel, f"{vehicle_count} vehicles", (8, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        timer_color = SIGNAL_COLORS[signal_state]
        cv2.putText(panel, f"{time_remaining}s", (8, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, timer_color, 2)

        return panel

    def _draw_side_panel(self, controller):
        panel = np.zeros((self.lane_h * 2, self.panel_w, 3), dtype=np.uint8)
        panel[:] = (18, 18, 18)

        cv2.putText(panel, "SYSTEM STATUS", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        uptime = int(time.time() - self.start_time)
        h, m, s = uptime // 3600, (uptime % 3600) // 60, uptime % 60
        cv2.putText(panel, f"Uptime: {h:02d}:{m:02d}:{s:02d}", (10, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (150, 150, 150), 1)

        mode_color = (0, 180, 255) if controller.manual_mode else (0, 220, 100)
        mode_text = "MANUAL" if controller.manual_mode else "ADAPTIVE"
        cv2.putText(panel, f"Mode: {mode_text}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, mode_color, 1)

        cv2.putText(panel, f"Cycles: {controller.cycle_count}", (10, 102),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (200, 200, 200), 1)

        cv2.line(panel, (10, 115), (self.panel_w - 10, 115), (60, 60, 60), 1)

        cv2.putText(panel, "LANE DETAILS", (10, 138),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        y = 165
        for i, signal in enumerate(controller.signals):
            state_color = SIGNAL_COLORS[signal.state]
            cv2.circle(panel, (18, y - 4), 7, state_color, -1)

            cong = controller.get_congestion_level(i)
            count = controller.lane_counts[i]
            cleared = signal.total_vehicles_cleared

            cv2.putText(panel, f"Lane {i+1}  {signal.state.value:<7}  {count:>2} veh",
                        (32, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1)
            cv2.putText(panel, f"  Cleared: {cleared}   Congestion: {cong}",
                        (32, y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 140, 140), 1)

            bar_w = int((count / max(controller.HIGH_CONGESTION_THRESHOLD, 1)) * (self.panel_w - 50))
            bar_w = min(bar_w, self.panel_w - 50)
            cv2.rectangle(panel, (32, y + 22), (32 + bar_w, y + 30), CONGESTION_COLORS[cong], -1)
            cv2.rectangle(panel, (32, y + 22), (self.panel_w - 18, y + 30), (60, 60, 60), 1)

            y += 72

        cv2.line(panel, (10, panel.shape[0] - 60), (self.panel_w - 10, panel.shape[0] - 60), (60, 60, 60), 1)
        cv2.putText(panel, "q:quit  s:stats  m:manual", (10, panel.shape[0] - 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (120, 120, 120), 1)
        cv2.putText(panel, "Place lane1-4.mp4 in /videos", (10, panel.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (80, 80, 80), 1)

        return panel

    def _draw_header(self, width):
        header = np.zeros((self.header_h, width, 3), dtype=np.uint8)
        header[:] = (15, 15, 15)
        cv2.putText(header, "REAL-TIME ADAPTIVE TRAFFIC MANAGEMENT SYSTEM",
                    (20, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)
        ts = time.strftime("%H:%M:%S")
        cv2.putText(header, ts, (width - 110, 33),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
        return header

    def render(self, frames, signals, lane_counts, controller):
        annotated = []
        for i, (frame, (state, remaining)) in enumerate(zip(frames, signals)):
            cong = controller.get_congestion_level(i)
            panel = self._draw_lane_panel(frame, state, remaining, lane_counts[i], i, cong)
            annotated.append(panel)

        row1 = np.hstack(annotated[:2]) if len(annotated) >= 2 else annotated[0]
        row2 = np.hstack(annotated[2:4]) if len(annotated) >= 4 else np.hstack(annotated[2:]) if len(annotated) > 2 else np.zeros_like(row1)

        lane_grid = np.vstack([row1, row2])

        side = self._draw_side_panel(controller)
        combined = np.hstack([lane_grid, side])

        header = self._draw_header(combined.shape[1])
        output = np.vstack([header, combined])

        return output
