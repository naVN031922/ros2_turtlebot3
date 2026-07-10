#!/usr/bin/env python3
# DECIDE stage: gate between AprilTag trigger and arm.
# On /apriltag_seen, checks TF for BOTH block detections; only then allows the arm.
import rclpy, time
from rclpy.node import Node
from std_msgs.msg import Bool
import tf2_ros

REQUIRED = ["green_block_detected", "blue_block_detected"]  # both must be detected
CHECK_TIMEOUT = 15.0   # seconds to wait for detections after AprilTag

class DetectionGate(Node):
    def __init__(self):
        super().__init__("detection_gate")
        # PERCEIVE(1): listen for the AprilTag trigger
        self.sub = self.create_subscription(Bool, "/apriltag_seen", self.on_apriltag, 10)
        # ACT: publish the go-signal to the arm sequencer
        self.pub = self.create_publisher(Bool, "/start_pick_and_place", 10)
        # PERCEIVE(2): TF listener to check block-detection frames
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.busy = False
        self.get_logger().info("Detection gate ready. Waiting for AprilTag (/apriltag_seen)...")

    def block_detected(self, frame):
        # returns True if TF has a recent odom->frame transform
        try:
            self.tf_buffer.lookup_transform("odom", frame, rclpy.time.Time())
            return True
        except Exception:
            return False

    def on_apriltag(self, msg):
        if not msg.data or self.busy:
            return
        self.busy = True
        self.get_logger().info("AprilTag seen -> DECIDE: checking both blocks are detected...")
        start = time.time()
        # DECIDE: wait until BOTH blocks are detected, or timeout
        while time.time() - start < CHECK_TIMEOUT:
            found = {f: self.block_detected(f) for f in REQUIRED}
            if all(found.values()):
                self.get_logger().info("BOTH blocks detected -> GATE OPEN -> starting arm")
                out = Bool(); out.data = True; self.pub.publish(out)
                self.busy = False
                return
            missing = [f for f, ok in found.items() if not ok]
            self.get_logger().info(f"Waiting... not yet detected: {missing}")
            time.sleep(1.0)
        # timeout: detection failed, gate stays closed
        self.get_logger().warn("TIMEOUT: not all blocks detected -> GATE CLOSED, arm will NOT run")
        self.busy = False

def main():
    rclpy.init()
    node = DetectionGate()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
