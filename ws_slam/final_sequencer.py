#!/usr/bin/env python3
# Two-block sequencer: BOTH blocks on table together, then pick each one by one.
import rclpy, time, threading
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import Bool, String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import GripperCommand
from gazebo_msgs.srv import SpawnEntity, DeleteEntity

SDF = "/ws_slam/objects/{}_block.sdf"
UP = [0.0, -1.0, 0.7, 0.3]
GOPEN, GNARROW, GCLOSE = 0.019, 0.004, -0.006
SETTLE, GRIP_W, PAD = 2.5, 2.5, 2.5

# Both blocks spawned on table FIRST (together), then picked one by one
SPAWN = [("green", (-1.837, -0.47, 0.086)), ("blue", (-1.837, -0.53, 0.086))]

BLOCKS = [
    {"color": "green",
     "above": [0.13, 0.9, -0.85, 1.45], "lower": [0.13, 0.85, -0.6, 1.25],
     "lift": [0.13, 0.0, 0.2, 1.3], "rotate": [1.3, 0.0, 0.2, 1.3],
     "descend": [1.3, 0.82, -0.02, 0.7], "place": [1.3, 0.87, -0.04, 0.67]},
    {"color": "blue",
     "above": [-0.13, 0.82, -0.78, 1.46], "lower": [-0.13, 0.85, -0.6, 1.25],
     "lift": [-0.13, 0.0, 0.2, 1.3], "rotate": [0.8, 0.0, 0.2, 1.3],
     "extend": [0.8, 0.7, -0.6, 1.4],
     "descend": [0.8, 0.82, -0.02, 0.7], "place": [0.8, 0.87, -0.04, 0.67]},
]

class FinalSeq(Node):
    def __init__(self):
        super().__init__("final_sequencer")
        self.sub = self.create_subscription(Bool, "/start_pick_and_place", self.on_trig, 10)
        self.arm = self.create_publisher(JointTrajectory, "/arm_controller/joint_trajectory", 10)
        self.att = self.create_publisher(String, "/attach", 10)
        self.det = self.create_publisher(String, "/detach", 10)
        self.grip = ActionClient(self, GripperCommand, "/gripper_controller/gripper_cmd")
        self.spawn = self.create_client(SpawnEntity, "/spawn_entity")
        self.delete = self.create_client(DeleteEntity, "/delete_entity")
        self.go = False; self.busy = False
        self.get_logger().info("Final sequencer ready. Waiting for /start_pick_and_place...")

    def on_trig(self, m):
        if m.data and not self.busy:
            self.get_logger().info("TRIGGER received -> running two-block pick-and-place")
            self.go = True

    def move(self, pos, sec=4):
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

    def spawn_block(self, c, xyz):
        d = DeleteEntity.Request(); d.name = f"{c}_block"; self.delete.call_async(d); time.sleep(1.0)
        s = SpawnEntity.Request(); s.name = f"{c}_block"; s.xml = open(SDF.format(c)).read()
        s.initial_pose.position.x, s.initial_pose.position.y, s.initial_pose.position.z = xyz
        self.spawn.call_async(s); time.sleep(SETTLE)

    def pubs(self, pub, txt):
        m = String(); m.data = txt; pub.publish(m); time.sleep(1.5)

    def do_block(self, b):
        c = b["color"]
        self.get_logger().info(f"=== {c.upper()}: grip ===")
        self.gripper(GNARROW); self.move(b["above"]); self.move(b["lower"]); self.gripper(GCLOSE)
        self.pubs(self.att, f"turtlebot3_manipulation_system::gripper_left_link {c}_block")
        self.get_logger().info(f"=== {c.upper()}: carry ===")
        self.move(b["lift"]); self.move(b["rotate"], 5)
        if "extend" in b: self.move(b["extend"], 5)
        self.get_logger().info(f"=== {c.upper()}: place ===")
        self.move(b["descend"], 5); self.move(b["place"], 4)
        self.pubs(self.det, "release"); self.gripper(GOPEN)
        self.move(b["rotate"], 4); self.move(UP, 4)
        self.get_logger().info(f"=== {c.upper()}: DONE ===")

    def run(self):
        self.busy = True
        # STEP 1: put BOTH blocks on the table together (arm up first)
        self.move(UP, 3)
        for c, xyz in SPAWN:
            self.spawn_block(c, xyz)
        self.get_logger().info("=== Both blocks on table. Now picking one by one ===")
        # STEP 2: pick each block one by one (blocks already on table together)
        for b in BLOCKS:
            self.do_block(b)
        self.get_logger().info("=== BOTH BLOCKS PLACED AT SEPARATE SPOTS - DONE ===")
        self.busy = False; self.go = False

def main():
    rclpy.init(); n = FinalSeq()
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
