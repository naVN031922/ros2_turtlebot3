#!/usr/bin/env python3
# Attach node: makes the block follow the gripper (models a rigid grasp).
# Reads gripper position via TF, re-spawns the block there continuously.
import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from gazebo_msgs.srv import DeleteEntity, SpawnEntity
import time

BLOCK = "red_block"
BLOCK_SDF = "/ws_slam/objects/red_block.sdf"

class AttachNode(Node):
    def __init__(self):
        super().__init__("attach_node")
        # TF listener: lets us look up where the gripper is
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        # service clients: to delete and spawn the block
        self.del_cli = self.create_client(DeleteEntity, "/delete_entity")
        self.spawn_cli = self.create_client(SpawnEntity, "/spawn_entity")
        self.del_cli.wait_for_service()
        self.spawn_cli.wait_for_service()
        with open(BLOCK_SDF) as f:
            self.sdf = f.read()
        # timer: run follow_step 6 times per second (every 0.15s)
        self.timer = self.create_timer(0.15, self.follow_step)
        self.get_logger().info("Attach node running - block will follow the gripper. Ctrl+C to release.")

    def gripper_position(self):
        # look up the gripper (end_effector_link) in the world (odom) frame
        try:
            t = self.tf_buffer.lookup_transform("odom", "end_effector_link", rclpy.time.Time())
            return (t.transform.translation.x, t.transform.translation.y, t.transform.translation.z)
        except Exception:
            return None  # TF not ready yet

    def follow_step(self):
        pos = self.gripper_position()
        if pos is None:
            return
        x, y, z = pos
        # delete the block from its old spot
        dr = DeleteEntity.Request(); dr.name = BLOCK
        self.del_cli.call_async(dr)
        # spawn it at the gripper position (slightly below grasp center so it sits in fingers)
        sr = SpawnEntity.Request()
        sr.name = BLOCK
        sr.xml = self.sdf
        sr.initial_pose.position.x = float(x)
        sr.initial_pose.position.y = float(y)
        sr.initial_pose.position.z = float(z)
        self.spawn_cli.call_async(sr)

def main():
    rclpy.init()
    node = AttachNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
