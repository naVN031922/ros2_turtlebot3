#!/usr/bin/env python3
"""AprilTag id 0 -> fire pick-and-place ONCE. Tag STAYS (not removed). Author: Naveen"""
import rclpy
from rclpy.node import Node
from apriltag_msgs.msg import AprilTagDetectionArray
from std_msgs.msg import Bool

TARGET_TAG_ID = 0

class AprilTagTriggerKeep(Node):
    def __init__(self):
        super().__init__("apriltag_trigger_keep")
        self.sub = self.create_subscription(
            AprilTagDetectionArray, "/detections", self.on_detections, 10)
        self.pub = self.create_publisher(Bool, "/start_pick_and_place", 10)
        self.already_fired = False   # one-shot guard: fire once, then ignore forever
        self.get_logger().info(f"Watching /detections for tag id {TARGET_TAG_ID} (fire once, tag stays)...")

    def on_detections(self, msg):
        # one-shot guard: if we already fired, ignore all further detections
        if self.already_fired:
            return
        found = any(d.id == TARGET_TAG_ID for d in msg.detections)
        if not found:
            return
        # lock immediately so repeated detections of the still-visible tag do nothing
        self.already_fired = True
        out = Bool(); out.data = True
        self.pub.publish(out)
        self.get_logger().info(f"Tag {TARGET_TAG_ID} detected -> fired /start_pick_and_place (tag stays in scene)")

def main():
    rclpy.init()
    node = AprilTagTriggerKeep()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
