from traffic.detector import VehicleDetector
from traffic.signal_controller import SignalController
from traffic.camera import CameraManager
from traffic.display import DisplayManager
import cv2
import time

def main():
    cameras = CameraManager(num_lanes=4)
    detector = VehicleDetector()
    controller = SignalController(num_lanes=4)
    display = DisplayManager()

    print("Traffic Management System Started")
    print("Press 'q' to quit | 's' to show stats | 'm' to toggle manual mode")

    while True:
        frames = cameras.read_frames()
        if frames is None:
            break

        lane_counts = []
        processed_frames = []

        for lane_id, frame in enumerate(frames):
            count, annotated = detector.detect(frame, lane_id)
            lane_counts.append(count)
            processed_frames.append(annotated)

        controller.update(lane_counts)
        signals = controller.get_signal_states()

        output = display.render(processed_frames, signals, lane_counts, controller)
        cv2.imshow("Traffic Management System", output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            controller.print_stats()
        elif key == ord('m'):
            controller.toggle_manual_mode()

    cameras.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
