# 🚦 Real-Time Adaptive Traffic Management System

A Python-based real-time traffic management system using **OpenCV** that monitors live camera feeds across multiple lanes, detects and counts vehicles, and dynamically adjusts signal timings using an **adaptive control algorithm** — giving longer green time to congested lanes automatically.

---

![Python](https://img.shields.io/badge/Python-3.7+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Mode](https://img.shields.io/badge/Mode-Adaptive%20%7C%20Manual-orange)

---

## Features

- 🎥 **Multi-Lane Camera Support** — connects to up to 4 live cameras or video files simultaneously
- 🚗 **Vehicle Detection** — detects and classifies vehicles (car, truck, bus) using background subtraction and contour analysis
- 🧠 **Adaptive Signal Control** — dynamically calculates green light duration based on real-time vehicle count per lane
- 🔴🟡🟢 **Signal State Visualization** — live signal display per lane with countdown timer
- 📊 **Congestion Level Monitor** — LOW / MEDIUM / HIGH congestion per lane with color-coded bar graph
- 🖥️ **Live Dashboard** — unified 4-lane grid view with system status side panel
- 🕹️ **Manual Override Mode** — toggle between adaptive and manual control at runtime
- 🔄 **Simulated Feed Fallback** — runs fully without cameras using built-in lane simulation

---

## System Architecture

```
main.py
  ├── CameraManager     → reads frames from cameras or video files (with simulation fallback)
  ├── VehicleDetector   → background subtraction + contour detection per lane
  ├── SignalController  → adaptive green time calculation, phase transitions, manual mode
  └── DisplayManager    → renders 4-lane grid + side panel dashboard
```

---

## Project Structure

```
traffic-management-system/
│
├── main.py                      # Entry point
├── config.py                    # All tunable parameters
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
│
├── traffic/
│   ├── __init__.py
│   ├── camera.py                # Multi-camera / video / simulation manager
│   ├── detector.py              # Vehicle detection and classification
│   ├── signal_controller.py     # Adaptive signal timing logic
│   └── display.py               # Full dashboard rendering
│
└── videos/                      # Optional: place lane1.mp4 ... lane4.mp4 here
    ├── lane1.mp4
    ├── lane2.mp4
    ├── lane3.mp4
    └── lane4.mp4
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/traffic-management-system.git
cd traffic-management-system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the System

```bash
python main.py
```

The system will:
1. Try to open `videos/lane1.mp4` through `lane4.mp4`
2. Fall back to connected webcams (`/dev/video0` etc.) if videos are missing
3. Use **built-in simulation** for any lane with no camera or video file

No hardware or video files are required to run the system out of the box.

---

## Runtime Controls

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `s` | Print lane statistics to terminal |
| `m` | Toggle adaptive ↔ manual mode |

---

## Adaptive Signal Algorithm

Green time for each lane is calculated as:

```
green_time = BASE_GREEN_TIME + (vehicle_count / VEHICLES_PER_SECOND)
green_time = clamp(green_time, MIN_GREEN_TIME, MAX_GREEN_TIME)
```

The controller always selects the **most congested waiting lane** as the next to receive green, not simply round-robin.

**Signal Phase Flow:**
```
GREEN (adaptive duration) → YELLOW (3s) → RED → next lane gets GREEN
```

---

## Congestion Levels

| Level | Vehicle Count |
|-------|--------------|
| LOW | < 10 |
| MEDIUM | 10 – 19 |
| HIGH | ≥ 20 |

---

## Configuration

All key parameters are in `config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `NUM_LANES` | `4` | Number of lanes/cameras |
| `BASE_GREEN_TIME` | `10` s | Minimum base green time |
| `MAX_GREEN_TIME` | `60` s | Maximum green time cap |
| `MIN_GREEN_TIME` | `5` s | Minimum green time floor |
| `YELLOW_TIME` | `3` s | Fixed yellow phase duration |
| `VEHICLES_PER_SECOND` | `0.5` | Assumed vehicle clearance rate |
| `CONGESTION_THRESHOLD` | `10` | MEDIUM congestion threshold |
| `HIGH_CONGESTION_THRESHOLD` | `20` | HIGH congestion threshold |
| `MIN_VEHICLE_AREA` | `1200` | Min contour area to count as vehicle |
| `MAX_VEHICLE_AREA` | `80000` | Max contour area (filters noise) |

---

## Using Real Camera Feeds

To use live webcams, edit `config.py`:

```python
VIDEO_SOURCES = [0, 1, 2, 3]   # webcam indices
```

To use video files:

```python
VIDEO_SOURCES = [
    "videos/lane1.mp4",
    "videos/lane2.mp4",
    "videos/lane3.mp4",
    "videos/lane4.mp4",
]
```

Mix and match — any missing source falls back to simulation automatically.

---

## Dashboard Preview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│          REAL-TIME ADAPTIVE TRAFFIC MANAGEMENT SYSTEM          12:34:01     │
├────────────────────┬────────────────────┬───────────────────────────────────┤
│  Lane 1  [GREEN]   │  Lane 2  [RED]     │  SYSTEM STATUS                    │
│  ┌──────────────┐  │  ┌──────────────┐  │  Uptime:  00:12:34                │
│  │ 🚗 🚗 🚛    │  │  │ 🚗          │  │  Mode:    ADAPTIVE                │
│  │              │  │  │              │  │  Cycles:  24                      │
│  └──────────────┘  │  └──────────────┘  │                                   │
│  8 vehicles  12s   │  3 vehicles  28s   │  Lane 1  GREEN   8 veh            │
├────────────────────┼────────────────────┤  Lane 2  RED     3 veh            │
│  Lane 3  [RED]     │  Lane 4  [RED]     │  Lane 3  RED    15 veh            │
│  ...               │  ...               │  Lane 4  RED     6 veh            │
└────────────────────┴────────────────────┴───────────────────────────────────┘
```

---

## Troubleshooting

**Camera not opening** — ensure no other app is using the camera. Try index `1` or `2` in `VIDEO_SOURCES`.

**Low detection accuracy** — tune `MIN_VEHICLE_AREA` and `MAX_VEHICLE_AREA` in `config.py` based on your camera height and angle.

**All lanes show simulation** — this is expected when no cameras or video files are connected. Place `.mp4` files in the `videos/` folder to use real footage.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- [OpenCV](https://opencv.org/) — Computer vision and camera processing
- [NumPy](https://numpy.org/) — Array operations for frame processing
- MOG2 Background Subtractor — OpenCV's built-in adaptive background model
