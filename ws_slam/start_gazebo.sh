#!/bin/bash
source /opt/ros/humble/setup.bash
source /ws_slam/install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
# Tell Gazebo where to find our custom grasp plugin
export GAZEBO_PLUGIN_PATH=/ws_slam/install/gazebo_grasp_plugin/lib:$GAZEBO_PLUGIN_PATH
echo "Starting Gazebo with grasp plugin... WAIT 1-2 minutes for it to settle (RTF ~1.0)."
ros2 launch turtlebot3_manipulation_gazebo gazebo.launch.py world:=/ws_slam/worlds/grasp_world.world
