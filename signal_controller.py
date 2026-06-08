import time
from enum import Enum


class SignalState(Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class LaneSignal:
    def __init__(self, lane_id):
        self.lane_id = lane_id
        self.state = SignalState.RED
        self.time_remaining = 0
        self.green_duration = 10
        self.yellow_duration = 3
        self.red_duration = 30
        self.total_vehicles_cleared = 0
        self.green_count = 0


class SignalController:
    BASE_GREEN_TIME = 10
    MAX_GREEN_TIME = 60
    MIN_GREEN_TIME = 5
    YELLOW_TIME = 3
    VEHICLES_PER_SECOND = 0.5
    CONGESTION_THRESHOLD = 10
    HIGH_CONGESTION_THRESHOLD = 20

    def __init__(self, num_lanes=4):
        self.num_lanes = num_lanes
        self.signals = [LaneSignal(i) for i in range(num_lanes)]
        self.active_lane = 0
        self.phase = "GREEN"
        self.phase_start_time = time.time()
        self.current_green_duration = self.BASE_GREEN_TIME
        self.manual_mode = False
        self.lane_counts = [0] * num_lanes
        self.cycle_count = 0
        self.last_update = time.time()

        self.signals[0].state = SignalState.GREEN
        for i in range(1, num_lanes):
            self.signals[i].state = SignalState.RED

    def _calculate_green_time(self, vehicle_count):
        extra = vehicle_count * (1 / self.VEHICLES_PER_SECOND)
        duration = self.BASE_GREEN_TIME + extra
        return max(self.MIN_GREEN_TIME, min(self.MAX_GREEN_TIME, duration))

    def update(self, lane_counts):
        self.lane_counts = lane_counts
        now = time.time()
        elapsed = now - self.phase_start_time

        if self.manual_mode:
            return

        if self.phase == "GREEN":
            green_time = self._calculate_green_time(lane_counts[self.active_lane])
            self.current_green_duration = green_time
            self.signals[self.active_lane].time_remaining = max(0, int(green_time - elapsed))

            if elapsed >= green_time:
                self.signals[self.active_lane].state = SignalState.YELLOW
                self.phase = "YELLOW"
                self.phase_start_time = now

        elif self.phase == "YELLOW":
            self.signals[self.active_lane].time_remaining = max(0, int(self.YELLOW_TIME - elapsed))
            if elapsed >= self.YELLOW_TIME:
                self.signals[self.active_lane].state = SignalState.RED
                self.signals[self.active_lane].total_vehicles_cleared += lane_counts[self.active_lane]
                self.signals[self.active_lane].green_count += 1

                self.active_lane = self._next_lane()
                self.signals[self.active_lane].state = SignalState.GREEN
                self.phase = "GREEN"
                self.phase_start_time = now
                self.cycle_count += 1

        for i, signal in enumerate(self.signals):
            if i != self.active_lane:
                signal.state = SignalState.RED
                red_wait = self._estimate_red_wait(i)
                signal.time_remaining = red_wait

    def _next_lane(self):
        counts = self.lane_counts
        max_count = -1
        best_lane = (self.active_lane + 1) % self.num_lanes

        for i in range(self.num_lanes):
            if i == self.active_lane:
                continue
            if counts[i] > max_count:
                max_count = counts[i]
                best_lane = i

        return best_lane

    def _estimate_red_wait(self, lane_id):
        remaining_current = self.signals[self.active_lane].time_remaining
        return remaining_current + self.YELLOW_TIME + self.BASE_GREEN_TIME

    def get_signal_states(self):
        return [(s.state, s.time_remaining) for s in self.signals]

    def get_congestion_level(self, lane_id):
        count = self.lane_counts[lane_id]
        if count >= self.HIGH_CONGESTION_THRESHOLD:
            return "HIGH"
        elif count >= self.CONGESTION_THRESHOLD:
            return "MEDIUM"
        return "LOW"

    def toggle_manual_mode(self):
        self.manual_mode = not self.manual_mode
        status = "ON" if self.manual_mode else "OFF"
        print(f"Manual Mode: {status}")

    def manual_set_green(self, lane_id):
        if not self.manual_mode:
            return
        for i, signal in enumerate(self.signals):
            signal.state = SignalState.RED
        self.signals[lane_id].state = SignalState.GREEN
        self.active_lane = lane_id
        self.phase = "GREEN"
        self.phase_start_time = time.time()

    def print_stats(self):
        print("\n===== Signal Controller Stats =====")
        print(f"Total Cycles: {self.cycle_count}")
        print(f"Manual Mode : {self.manual_mode}")
        for i, signal in enumerate(self.signals):
            print(f"Lane {i+1}: State={signal.state.value} | Vehicles Cleared={signal.total_vehicles_cleared} | Green Cycles={signal.green_count}")
        print("===================================\n")
