#!/usr/bin/env python3
# Two-block ordered pick-and-place: GREEN -> Spot A, BLUE -> Spot B.
import rclpy, time, threading
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import Bool, String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import GripperCommand
from gazebo_msgs.srv import SpawnEntity, DeleteEntity

SDF = "/ws_slam/objects/{}_block.sdf"
STATION = (-1.837, -0.5, 0.086)
PLAN = [("green", 1.3), ("blue", 0.6)]
UP    = [0.0, -1.0, 0.7, 0.3]
GRASP = [0.0, 0.85, -0.6, 1.25]
GOPEN, GCLOSE = 0.019, -0.006
SETTLE, GRIP_W, PAD = 2.5, 2.5, 2.5

class TwoBlock(Node):
    def __init__(self):
        super().__init__("two_block_sequencer")
        self.sub = self.create_subscription(Bool, "/start_pick_and_place", self.on_trig, 10)
        self.arm = self.create_publisher(JointTrajectory, "/arm_controller/joint_trajectory", 10)
        self.att = self.create_publisher(String, "/attach", 10)
        self.det = self.create_publisher(String, "/detach", 10)
        self.grip = ActionClient(self, GripperCommand, "/gripper_controller/gripper_cmd")
        self.spawn = self.create_client(SpawnEntity, "/spawn_entity")
        self.delete = self.create_client(DeleteEntity, "/delete_entity")
        self.go = False; self.busy = False
        self.get_logger().info("Two-block sequencer ready. Waiting for /start_pick_and_place...")

    def on_trig(self, m):
        if m.data and not self.busy:
            self.get_logger().info("TRIGGER -> starting green+blue")
            self.go = True

    def move(self, pos, sec):
        t = JointTrajectory(); t.joint_names = ["joint1","joint2","joint3","joint4"]
        p = JointTrajectoryPoint(); p.positions = [float(x) for x in pos]
        p.time_from_start.sec = sec; t.points = [p]
        self.arm.publish(t); time.sleep(sec + PAD)

    def gripper(self, pos):
        g = GripperCommand.Goal(); g.command.position = float(pos); g.command.max_effort = 15.0
        self.grip.wait_for_server(); f = self.grip.send_goal_async(g)
        t0 = time.time()
        while not f.done() and time.time()-t0 < 5: time.sleep(0.1)
        time.sleep(GRIP_W)

    def spawn_block(self, c):
        d = DeleteEntity.Request(); d.name = f"{c}_block"; self.delete.call_async(d); time.sleep(1.0)
        s = SpawnEntity.Request(); s.name = f"{c}_block"; s.xml = open(SDF.format(c)).read()
        s.initial_pose.position.x = STATION[0]; s.initial_pose.position.y = STATION[1]
        s.initial_pose.position.z = STATION[2]; self.spawn.call_async(s); time.sleep(SETTLE)

    def pubs(self, pub, txt):
        m = String(); m.data = txt; pub.publish(m); time.sleep(1.5)

    def pick_place(self, color, dj1):
        self.get_logger().info(f"=== {color.upper()} : present ===")
        self.move(UP, 3); self.spawn_block(color)
        self.get_logger().info(f"=== {color.upper()} : grasp ===")
        self.gripper(GOPEN); self.move(GRASP, 4); self.gripper(GCLOSE)
        self.pubs(self.att, f"turtlebot3_manipulation_system::gripper_left_link {color}_block")
        self.get_logger().info(f"=== {color.upper()} : lift+carry j1={dj1} ===")
        self.move([dj1, 0.0, 0.2, 1.3], 5)
        self.get_logger().info(f"=== {color.upper()} : descend+release ===")
        self.move([dj1, 0.82, -0.02, 0.7], 6)
        self.pubs(self.det, "release"); self.gripper(GOPEN)
        self.move([dj1, 0.0, 0.2, 1.3], 4)
        self.move(UP, 4)
        self.get_logger().info(f"=== {color.upper()} : placed j1={dj1} ===")

    def run(self):
        self.busy = True
        for color, dj1 in PLAN:
            self.pick_place(color, dj1)
        self.get_logger().info("=== DONE: green and blue at separate spots ===")
        self.busy = False; self.go = False

def main():
    rclpy.init(); n = TwoBlock()
    ex = rclpy.executors.SingleThreadedExecutor(); ex.add_node(n)
    threading.Thread(target=ex.spin, daemon=True).start()
    try:
        while rclpy.ok():
            if n.go and not n.busy: n.run()
            time.sleep(0.2)
    except KeyboardInterrupt: pass
    rclpy.shutdown()

if __name__ == "__main__":
    main()
