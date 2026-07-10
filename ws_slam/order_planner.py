#!/usr/bin/env python3
# Order planner (Phase 1 brain):
# When the AprilTag triggers, it announces the fixed task order red -> blue -> green.
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String
from tf2_ros import Buffer, TransformListener

# The fixed task order (confirmed with professor: AprilTag triggers, order is fixed)
FIXED_ORDER = ["red", "blue", "green"]

class OrderPlanner(Node):
    def __init__(self):
        super().__init__("order_planner")
        # LISTEN: the AprilTag trigger (published by apriltag_trigger.py)
        self.trigger_sub = self.create_subscription(
            Bool, "/start_pick_and_place", self.on_trigger, 10)
        # BROADCAST: the task order for the arm (Phase 2) to execute
        self.order_pub = self.create_publisher(String, "/task_order", 10)
        # TF listener: lets us confirm which colored blocks were detected
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.get_logger().info("Order planner ready. Waiting for AprilTag trigger...")

    def detected_colors(self):
        # Check which color TF frames exist (published by color_pose_detector.py)
        found = []
        for color in FIXED_ORDER:
            try:
                self.tf_buffer.lookup_transform(
                    "odom", color + "_block_detected", rclpy.time.Time())
                found.append(color)
            except Exception:
                pass
        return found

    def on_trigger(self, msg):
        if not msg.data:
            return
        self.get_logger().info("=== AprilTag trigger received ===")
        # Confirm detections (informational)
        seen = self.detected_colors()
        self.get_logger().info(f"Colors currently detected by camera: {seen}")
        # Announce the fixed task order
        order_str = ",".join(FIXED_ORDER)
        self.get_logger().info(f"TASK ORDER: {order_str}")
        out = String()
        out.data = order_str
        self.order_pub.publish(out)
        self.get_logger().info("Published task order to /task_order for the arm.")

def main():
    rclpy.init()
    node = OrderPlanner()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
