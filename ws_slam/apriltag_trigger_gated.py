#!/usr/bin/env python3
"""AprilTag id 0 -> publish /apriltag_seen (feeds the detection gate). Author: Naveen"""
import rclpy
from rclpy.node import Node
from apriltag_msgs.msg import AprilTagDetectionArray
from std_msgs.msg import Bool
TARGET_TAG_ID = 0
COOLDOWN_SEC = 10.0
class AprilTagTrigger(Node):
    def __init__(self):
        super().__init__("apriltag_trigger_gated")
        self.sub = self.create_subscription(
            AprilTagDetectionArray, "/detections", self.on_detections, 10)
        self.pub = self.create_publisher(Bool, "/apriltag_seen", 10)
        self.last_trigger_time = None
        self.get_logger().info(f"Watching /detections for tag id {TARGET_TAG_ID} -> /apriltag_seen")
    def on_detections(self, msg):
        found = any(d.id == TARGET_TAG_ID for d in msg.detections)
        if not found:
            return
        now = self.get_clock().now()
        if self.last_trigger_time is not None:
            elapsed = (now - self.last_trigger_time).nanoseconds / 1e9
            if elapsed < COOLDOWN_SEC:
                return
        self.last_trigger_time = now
        self.get_logger().info(f"Tag {TARGET_TAG_ID} seen -> publishing /apriltag_seen")
        out = Bool(); out.data = True
        self.pub.publish(out)
def main():
    rclpy.init()
    node = AprilTagTrigger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == "__main__":
    main()
