# Selective Multi-Object Pick-and-Place on TurtleBot3 with OpenMANIPULATOR-X Triggered by AprilTag Detection

**Developed by:** Naveen Kurakula (12504369)
Deggendorf Institute of Technology, Campus Cham

## Description

An autonomous, AprilTag-triggered fixed pick-and-place system for the TurtleBot3 Waffle Pi with an OpenMANIPULATOR-X arm, in ROS 2 (Humble) and Gazebo Classic. On detecting an AprilTag, the arm selectively picks two colored blocks from a table and places them at two separate floor locations, using a custom grasp plugin, color detection, and smooth motion.

## Features 

- Custom C++ Gazebo grasp plugin for a reliable rigid grasp (fixed joint).
- Selective two-block pick-and-place: picks one block without disturbing its neighbour.
- AprilTag (36h11) detection used as a one-shot task trigger.
- OpenCV HSV color detection publishing 3D object poses as TF frames.
- Smooth multi-waypoint arm motion (teach-and-repeat).
- Single-command launch of the whole pipeline (perceive-decide-act).

## Technologies Used

- ROS 2 (Humble)
- Gazebo Classic
- Python
- C++ (Gazebo plugin)
- OpenCV
- AprilTag (apriltag_ros)

## Project Structure

```
ws_slam/
│
├── src/
│   └── gazebo_grasp_plugin/          # custom C++ grasp plugin
│       ├── src/grasp_plugin.cpp
│       ├── CMakeLists.txt
│       └── package.xml
│
├── objects/
│   ├── color_pose_detector.py        # OpenCV HSV detection -> TF
│   ├── green_block.sdf
│   ├── blue_block.sdf
│   ├── red_block.sdf
│   └── reach_table.sdf
│
├── apriltag_config/                  # AprilTag detector config
│   └── tags.yaml
├── apriltag_marker/                  # AprilTag marker model
│   └── model.sdf
├── worlds/
│   └── grasp_world.world             # Gazebo world with grasp plugin
│
├── smooth_sequencer.py               # two-block selective pick-and-place
├── full_demo.launch.py               # single-command launch of the demo
├── apriltag_trigger_keep.py          # AprilTag trigger (fires once, tag stays)
├── apriltag_trigger_once.py          # AprilTag trigger (fires once, removes tag)
├── detection_gate.py                 # perception gate (detect-then-act)
├── start_gazebo.sh                   # helper script
├── DEMO_PICK_PLACE.txt               # recorded verified poses
└── README.md                         # project documentation
```
## Running the Simulation

### Terminal 1 — Launch Gazebo

Start the simulation and wait for it to settle.

```bash
bash /ws_slam/start_gazebo.sh
```

### Terminal 2 — Launch the Pick-and-Place Pipeline

Source the workspace, then launch the whole demo with one command.

```bash
source /opt/ros/humble/setup.bash
source /ws_slam/install/setup.bash
ros2 launch /ws_slam/full_demo.launch.py
```

The launch spawns the table, starts the AprilTag detector and the sequencer, then spawns the AprilTag. On detection, the trigger fires once and the arm performs a single two-block selective pick-and-place, placing each block at a separate floor location.
## Demo

🎥 [Click here to watch the demo](https://youtu.be/ou3yh9TIXOA)
