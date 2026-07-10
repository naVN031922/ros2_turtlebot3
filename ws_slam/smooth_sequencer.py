#!/usr/bin/env python3
# Smooth two-block sequencer: both blocks on table, each carry-place is ONE continuous motion.
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

SPAWN = [("green", (-1.837, -0.47, 0.086)), ("blue", (-1.837, -0.53, 0.086))]

# Each block: approach waypoints (to grip), carry waypoints (to place). One smooth motion each.
BLOCKS = [
    {"color": "green",
     "approach": [[0.13, 0.9, -0.85, 1.45], [0.13, 0.85, -0.6, 1.25]],
     "carry": [[0.13, 0.0, 0.2, 1.3], [1.3, 0.0, 0.2, 1.3],
               [1.3, 0.82, -0.02, 0.7], [1.3, 0.87, -0.04, 0.67]]},
    {"color": "blue",
     "approach": [[-0.13, 0.82, -0.78, 1.46], [-0.13, 0.85, -0.6, 1.25]],
     "carry": [[-0.13, 0.0, 0.2, 1.3], [0.8, 0.0, 0.2, 1.3], [0.8, 0.7, -0.6, 1.4],
               [0.8, 0.82, -0.02, 0.7], [0.8, 0.87, -0.04, 0.67]]},
]

class SmoothSeq(Node):
    def __init__(self):
        super().__init__("smooth_sequencer")
        self.sub = self.create_subscription(Bool, "/start_pick_and_place", self.on_trig, 10)
        self.arm = self.create_publisher(JointTrajectory, "/arm_controller/joint_trajectory", 10)
        self.att = self.create_publisher(String, "/attach", 10)
        self.det = self.create_publisher(String, "/detach", 10)
        self.grip = ActionClient(self, GripperCommand, "/gripper_controller/gripper_cmd")
        self.spawn = self.create_client(SpawnEntity, "/spawn_entity")
        self.delete = self.create_client(DeleteEntity, "/delete_entity")
        self.go = False; self.busy = False
        self.get_logger().info("Smooth sequencer ready. Waiting for /start_pick_and_place...")

    def on_trig(self, m):
        if m.data and not self.busy:
            self.get_logger().info("TRIGGER -> smooth two-block pick-and-place")
            self.go = True

    def move_one(self, pos, sec=4):
        # single waypoint (for simple moves like UP)
        t = JointTrajectory(); t.joint_names = ["joint1","joint2","joint3","joint4"]
        p = JointTrajectoryPoint(); p.positions=[float(x) for x in pos]
        p.time_from_start.sec = sec; t.points=[p]
        self.arm.publish(t); time.sleep(sec + 1.5)

    def move_smooth(self, waypoints, step=4):
        # MULTIPLE waypoints in ONE message -> continuous flowing motion
        t = JointTrajectory(); t.joint_names = ["joint1","joint2","joint3","joint4"]
        tt = 0
        for wp in waypoints:
            tt += step
            p = JointTrajectoryPoint(); p.positions=[float(x) for x in wp]
            p.time_from_start.sec = tt; t.points.append(p)
        self.arm.publish(t)
        time.sleep(tt + 2.0)   # wait for the whole smooth motion to finish

    def gripper(self, pos):
        g = GripperCommand.Goal(); g.command.position=float(pos); g.command.max_effort=15.0
        self.grip.wait_for_server(); f=self.grip.send_goal_async(g)
        t0=time.time()
        while not f.done() and time.time()-t0<5: time.sleep(0.1)
        time.sleep(2.0)

    def spawn_block(self, c, xyz):
        d=DeleteEntity.Request(); d.name=f"{c}_block"; self.delete.call_async(d); time.sleep(1.0)
        s=SpawnEntity.Request(); s.name=f"{c}_block"; s.xml=open(SDF.format(c)).read()
        s.initial_pose.position.x, s.initial_pose.position.y, s.initial_pose.position.z = xyz
        self.spawn.call_async(s); time.sleep(2.5)

    def pubs(self, pub, txt):
        m=String(); m.data=txt; pub.publish(m); time.sleep(1.5)

    def do_block(self, b):
        c=b["color"]
        self.get_logger().info(f"=== {c.upper()}: approach + grip ===")
        self.gripper(GNARROW)
        self.move_smooth(b["approach"], step=4)     # smooth approach to block
        self.gripper(GCLOSE)                          # grip
        self.pubs(self.att, f"turtlebot3_manipulation_system::gripper_left_link {c}_block")
        self.get_logger().info(f"=== {c.upper()}: smooth carry + place ===")
        self.move_smooth(b["carry"], step=4)          # ONE smooth carry-and-place motion
        self.pubs(self.det, "release"); self.gripper(GOPEN)
        self.move_one(UP, 4)
        self.get_logger().info(f"=== {c.upper()}: DONE ===")

    def run(self):
        self.busy=True
        self.move_one(UP, 3)
        for c,xyz in SPAWN: self.spawn_block(c, xyz)
        self.get_logger().info("=== Both blocks on table, picking one by one ===")
        for b in BLOCKS: self.do_block(b)
        self.get_logger().info("=== DONE: both placed at separate spots ===")
        self.busy=False; self.go=False

def main():
    rclpy.init(); n=SmoothSeq()
    ex=rclpy.executors.SingleThreadedExecutor(); ex.add_node(n)
    threading.Thread(target=ex.spin, daemon=True).start()
    try:
        while rclpy.ok():
            if n.go and not n.busy: n.run()
            time.sleep(0.2)
    except KeyboardInterrupt: pass
    rclpy.shutdown()

if __name__=="__main__":
    main()
