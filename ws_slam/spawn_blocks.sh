#!/bin/bash
ros2 run gazebo_ros spawn_entity.py -entity red_block -file /ws_slam/objects/red_block.sdf -x -1.4 -y -0.45 -z 0.05
ros2 run gazebo_ros spawn_entity.py -entity blue_block -file /ws_slam/objects/blue_block.sdf -x -1.4 -y -0.50 -z 0.05
ros2 run gazebo_ros spawn_entity.py -entity green_block -file /ws_slam/objects/green_block.sdf -x -1.4 -y -0.55 -z 0.05
echo "Three blocks spawned."
