#!/usr/bin/env python3
# Fully-automatic demo: spawns table + nodes + tag (tag STAYS) -> runs ONCE.
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, TimerAction

def generate_launch_description():
    apriltag = Node(
        package="apriltag_ros", executable="apriltag_node", name="apriltag_node",
        remappings=[("image_rect", "/pi_camera/image_raw"),
                    ("camera_info", "/pi_camera/camera_info")],
        parameters=["/ws_slam/apriltag_config/tags.yaml"], output="screen")

    sequencer = ExecuteProcess(
        cmd=["python3", "/ws_slam/smooth_sequencer.py"], output="screen")

    spawn_table = ExecuteProcess(
        cmd=["ros2", "run", "gazebo_ros", "spawn_entity.py",
             "-entity", "reach_table", "-file", "/ws_slam/objects/reach_table.sdf",
             "-x", "-1.837", "-y", "-0.5", "-z", "0.0355"], output="screen")

    # run-once trigger that KEEPS the tag (does not remove it)
    trigger = TimerAction(period=5.0, actions=[
        ExecuteProcess(cmd=["python3", "/ws_slam/apriltag_trigger_keep.py"], output="screen")])

    # spawn the tag at 10s -> triggers once -> tag STAYS in the scene
    spawn_tag = TimerAction(period=10.0, actions=[
        ExecuteProcess(cmd=["ros2", "run", "gazebo_ros", "spawn_entity.py",
             "-entity", "apriltag", "-file", "/ws_slam/apriltag_marker/model.sdf",
             "-x", "-1.45", "-y", "-0.5", "-z", "0.15"], output="screen")])

    return LaunchDescription([apriltag, sequencer, spawn_table, trigger, spawn_tag])
