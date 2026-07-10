#!/bin/bash
source /opt/ros/humble/setup.bash
source /ws_slam/install/setup.bash
echo "Starting the autonomous pipeline (detector + arm + bridge + tag)..."
ros2 launch /ws_slam/src/pymoveit2/examples/demo_pipeline.launch.py
