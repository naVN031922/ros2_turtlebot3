#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np
import cv2

class ColorDetector(Node):
    def __init__(self):
        super().__init__('color_detector')
        self.sub = self.create_subscription(Image, '/pi_camera/image_raw', self.cb, 10)
        self.colors = {
            'red':   [(0, 100, 100),   (10, 255, 255)],
            'red2':  [(160, 100, 100), (179, 255, 255)],
            'blue':  [(100, 100, 100), (130, 255, 255)],
            'green': [(40, 100, 100),  (80, 255, 255)],
        }
        self.get_logger().info('Color detector started.')

    def cb(self, msg):
        img = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, 3)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        found = []
        for name, ranges in [('red', ['red','red2']), ('blue',['blue']), ('green',['green'])]:
            mask = None
            for r in ranges:
                lo, hi = self.colors[r]
                m = cv2.inRange(hsv, np.array(lo), np.array(hi))
                mask = m if mask is None else (mask | m)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                area = cv2.contourArea(c)
                if area > 100:
                    M = cv2.moments(c)
                    if M['m00'] > 0:
                        cx = int(M['m10']/M['m00'])
                        cy = int(M['m01']/M['m00'])
                        found.append(name + ' at (' + str(cx) + ',' + str(cy) + ') area=' + str(int(area)))
        if found:
            self.get_logger().info('Detected: ' + ' | '.join(found))
        else:
            self.get_logger().info('No colored blocks detected')

def main():
    rclpy.init()
    node = ColorDetector()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
