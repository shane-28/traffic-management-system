import cv2
import numpy as np
import os


class CameraManager:
    def __init__(self, num_lanes=4, sources=None):
        self.num_lanes = num_lanes
        self.captures = []
        self.frame_size = (320, 240)

        if sources is None:
            sources = self._auto_detect_sources()

        for src in sources:
            cap = cv2.VideoCapture(src)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_size[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_size[1])
                self.captures.append(cap)
            else:
                self.captures.append(None)

        print(f"Initialized {len(self.captures)} camera(s). Missing cameras use simulation.")

    def _auto_detect_sources(self):
        video_files = []
        for i in range(self.num_lanes):
            path = f"videos/lane{i+1}.mp4"
            if os.path.exists(path):
                video_files.append(path)
            else:
                video_files.append(i)
        return video_files

    def _simulate_frame(self, lane_id):
        frame = np.zeros((self.frame_size[1], self.frame_size[0], 3), dtype=np.uint8)
        frame[:] = (30, 30, 30)

        cv2.putText(frame, f"Lane {lane_id + 1}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 2)
        cv2.putText(frame, "Simulated Feed", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 100), 1)

        import time
        t = time.time()
        num_vehicles = int(3 + lane_id * 2 + (np.sin(t * 0.3 + lane_id) + 1) * 3)
        np.random.seed(int(t * 2) + lane_id * 100)
        for _ in range(num_vehicles):
            x = np.random.randint(10, self.frame_size[0] - 60)
            y = np.random.randint(60, self.frame_size[1] - 40)
            w = np.random.randint(30, 70)
            h = np.random.randint(20, 45)
            color = (
                np.random.randint(100, 255),
                np.random.randint(100, 255),
                np.random.randint(100, 255)
            )
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)

        return frame

    def read_frames(self):
        frames = []
        for i, cap in enumerate(self.captures):
            if cap is not None and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame, self.frame_size)
                    frames.append(frame)
                else:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frames.append(self._simulate_frame(i))
            else:
                frames.append(self._simulate_frame(i))
        return frames

    def release(self):
        for cap in self.captures:
            if cap is not None:
                cap.release()
