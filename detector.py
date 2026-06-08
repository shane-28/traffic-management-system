import cv2
import numpy as np


class VehicleDetector:
    def __init__(self):
        self.bg_subtractors = {}
        self.min_area = 1200
        self.max_area = 80000
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.vehicle_colors = {
            "car": (0, 255, 0),
            "truck": (0, 165, 255),
            "bus": (0, 0, 255),
            "unknown": (255, 255, 0),
        }

    def _get_subtractor(self, lane_id):
        if lane_id not in self.bg_subtractors:
            self.bg_subtractors[lane_id] = cv2.createBackgroundSubtractorMOG2(
                history=500, varThreshold=50, detectShadows=True
            )
        return self.bg_subtractors[lane_id]

    def _classify_vehicle(self, area):
        if area < 4000:
            return "car"
        elif area < 15000:
            return "car"
        elif area < 35000:
            return "truck"
        else:
            return "bus"

    def detect(self, frame, lane_id):
        subtractor = self._get_subtractor(lane_id)
        fg_mask = subtractor.apply(frame)

        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, self.kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, self.kernel)
        thresh = cv2.dilate(thresh, self.kernel, iterations=2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        annotated = frame.copy()
        vehicle_count = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area < area < self.max_area:
                vehicle_count += 1
                x, y, w, h = cv2.boundingRect(contour)
                vehicle_type = self._classify_vehicle(area)
                color = self.vehicle_colors[vehicle_type]

                cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
                label = f"{vehicle_type}"
                cv2.putText(annotated, label, (x, y - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        return vehicle_count, annotated
