#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import numpy as np
import cv2

# Camera intrinsics (from /pi_camera/camera_info)
FX = FY = 530.4669406576809
CX, CY = 320.5, 240.5
# Camera pose in world (from tf odom->camera_rgb_optical_frame)
CAM_POS = np.array([-1.924, -0.500, 0.113])
R = np.array([[0.001,0.001,1.000],[-1.000,0.000,0.001],[0.000,-1.000,0.001]])
TARGET_Z = 0.01  # calibrated ground plane for block projection

class ColorPoseDetector(Node):
    def __init__(self):
        super().__init__("color_pose_detector")
        self.sub = self.create_subscription(Image, "/pi_camera/image_raw", self.cb, 10)
        self.br = TransformBroadcaster(self)
        self.colors = {
            "red":   [((0,80,80),(10,255,255)), ((160,80,80),(179,255,255))],
            "blue":  [((95,80,80),(135,255,255))],
            "green": [((35,80,80),(85,255,255))],
        }
        self.get_logger().info("Color pose detector started -> publishing TF frames")

    def pixel_to_world(self, u, v):
        ray_cam = np.array([(u-CX)/FX, (v-CY)/FY, 1.0])
        ray_world = R @ ray_cam
        t = (TARGET_Z - CAM_POS[2]) / ray_world[2]
        return CAM_POS + t*ray_world

    def cb(self, msg):
        img = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, 3)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        for name, ranges in self.colors.items():
            mask = None
            for lo, hi in ranges:
                m = cv2.inRange(hsv, np.array(lo), np.array(hi))
                mask = m if mask is None else (mask | m)
            cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            big = [c for c in cnts if cv2.contourArea(c) > 100]
            if big:
                c = max(big, key=cv2.contourArea)
                M = cv2.moments(c)
                u = int(M["m10"]/M["m00"]); v = int(M["m01"]/M["m00"])
                wx, wy, wz = self.pixel_to_world(u, v)
                tf = TransformStamped()
                tf.header.stamp = self.get_clock().now().to_msg()
                tf.header.frame_id = "odom"
                tf.child_frame_id = name + "_block_detected"
                tf.transform.translation.x = float(wx)
                tf.transform.translation.y = float(wy)
                tf.transform.translation.z = float(wz)
                tf.transform.rotation.w = 1.0
                self.br.sendTransform(tf)

def main():
    rclpy.init()
    node = ColorPoseDetector()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
