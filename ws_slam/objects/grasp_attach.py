#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from gazebo_msgs.srv import DeleteEntity, SpawnEntity
import subprocess, time, threading

BLOCK = "red_block"
BLOCK_SDF = "/ws_slam/objects/red_block.sdf"

class GraspAttach(Node):
    def __init__(self):
        super().__init__('grasp_attach')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.attached = False
        self.get_logger().info("Grasp attach node ready. Call attach()/detach() via terminal.")

    def gripper_world(self):
        # read end_effector_link in odom (world) frame
        try:
            t = self.tf_buffer.lookup_transform('odom', 'end_effector_link', rclpy.time.Time())
            return (t.transform.translation.x, t.transform.translation.y, t.transform.translation.z)
        except Exception as e:
            return None

def main():
    rclpy.init()
    node = GraspAttach()
    # spin in background so TF fills
    ex = rclpy.executors.SingleThreadedExecutor()
    ex.add_node(node)
    t = threading.Thread(target=ex.spin, daemon=True)
    t.start()
    time.sleep(2.0)  # let TF buffer fill

    # Track and keep block at gripper while "attached"
    print("Tracking gripper. The block will follow it. Ctrl+C to stop.")
    last = None
    try:
        while True:
            pos = node.gripper_world()
            if pos:
                x, y, z = pos
                # only move if gripper moved > 1cm (avoid spam)
                if last is None or abs(x-last[0])+abs(y-last[1])+abs(z-last[2]) > 0.01:
                    subprocess.run(["ros2","service","call","/delete_entity",
                        "gazebo_msgs/srv/DeleteEntity", f"{{name: '{BLOCK}'}}"],
                        capture_output=True)
                    subprocess.run(["ros2","run","gazebo_ros","spawn_entity.py",
                        "-entity",BLOCK,"-file",BLOCK_SDF,
                        "-x",str(x),"-y",str(y),"-z",str(z)],
                        capture_output=True)
                    last = (x,y,z)
            time.sleep(0.3)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()
