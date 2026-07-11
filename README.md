# Selective Multi-Object Pick-and-Place on TurtleBot3 with OpenMANIPULATOR-X Triggered by AprilTag Detection

**Author:** Naveen Kurakula (12504369)
Deggendorf Institute of Technology, Campus Cham

## Description

An autonomous, AprilTag-triggered fixed pick-and-place system for the TurtleBot3 Waffle Pi with an OpenMANIPULATOR-X arm, in ROS 2 (Humble) and Gazebo Classic. On detecting an AprilTag, the arm selectively picks two colored blocks from a table and places them at two separate floor locations, using a custom grasp plugin, color detection, and smooth motion.

## Main Features 

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

## My Work

Located under `ws_slam/`:

- `src/gazebo_grasp_plugin/` — custom C++ Gazebo grasp plugin (rigid grasp via a fixed joint)
- `smooth_sequencer.py` — two-block selective pick-and-place with smooth multi-waypoint motion
- `full_demo.launch.py` — single-command launch of the whole demo (table + nodes + tag)
- `apriltag_trigger_once.py`, `apriltag_trigger_keep.py`, `apriltag_trigger_gated.py` — AprilTag trigger nodes
- `detection_gate.py` — perception gate (detect-then-act)
- `order_planner.py`, `final_sequencer.py`, `two_block_sequencer.py`, `pick_sequencer.py` — sequencing logic
- `objects/color_pose_detector.py` — OpenCV HSV color detection publishing 3D TF frames
- `objects/` — block, table, and platform models (SDF)
- `apriltag_config/`, `apriltag_marker/` — AprilTag detector config and marker model
- `worlds/grasp_world.world` — Gazebo world with the grasp plugin loaded
- `DEMO_PICK_PLACE.txt` — recorded verified poses and notes
- `start_gazebo.sh`, `start_demo.sh`, `spawn_blocks.sh` — helper scripts

## Installation and Running

```bash
# 1. Start the simulation
bash start_gazebo.sh          # wait for Gazebo to settle

# 2. In another sourced terminal, launch the whole demo
ros2 launch /ws_slam/full_demo.launch.py
```

The launch spawns the table, starts the detector, sequencer, and trigger, then spawns the AprilTag, which triggers a single two-block pick-and-place.
