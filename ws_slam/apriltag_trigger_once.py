#!/usr/bin/env python3
"""AprilTag id 0 -> fire pick-and-place ONCE, then remove the tag. Author: Naveen"""
import rclpy
from rclpy.node import Node
from apriltag_msgs.msg import AprilTagDetectionArray
from std_msgs.msg import Bool
from gazebo_msgs.srv import DeleteEntity

TARGET_TAG_ID = 0
TAG_MODEL_NAME = "apriltag"   # the name of the marker in Gazebo

class AprilTagTriggerOnce(Node):
    def __init__(self):
        super().__init__("apriltag_trigger_once")
        # PERCEIVE: watch the detector output
        self.sub = self.create_subscription(
            AprilTagDetectionArray, "/detections", self.on_detections, 10)
        # ACT: publish the start signal
        self.pub = self.create_publisher(Bool, "/start_pick_and_place", 10)
        # a client to call Gazebo's delete service (to remove the tag)
        self.delete_client = self.create_client(DeleteEntity, "/delete_entity")
        # one-shot guard: once we fire, we never fire again
        self.already_fired = False
        self.get_logger().info(f"Watching /detections for tag id {TARGET_TAG_ID} (fire once)...")

    def on_detections(self, msg):
        # one-shot guard: if we already fired, ignore everything
        if self.already_fired:
            return
        found = any(d.id == TARGET_TAG_ID for d in msg.detections)
        if not found:
            return
        # lock immediately so stray detections cannot fire again
        self.already_fired = True

        # 1) fire the start signal
        out = Bool(); out.data = True
        self.pub.publish(out)
        self.get_logger().info(f"Tag {TARGET_TAG_ID} detected -> fired /start_pick_and_place")

        # 2) remove the tag so it cannot trigger again
        if self.delete_client.wait_for_service(timeout_sec=2.0):
            req = DeleteEntity.Request()
            req.name = TAG_MODEL_NAME
            self.delete_client.call_async(req)
            self.get_logger().info(f"Removed the AprilTag marker '{TAG_MODEL_NAME}'.")
        else:
            self.get_logger().warn("Delete service not available; tag not removed.")

def main():
    rclpy.init()
    node = AprilTagTriggerOnce()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
