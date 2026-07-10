#!/usr/bin/env python3
# Pick sequencer (Phase 2): for each color in order, pick from station, place on floor past wheel.
import rclpy, time, threading
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import Bool, String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import GripperCommand
from gazebo_msgs.srv import SpawnEntity, DeleteEntity

ORDER = ["green", "blue"]
SDF = "/ws_slam/objects/{}_block.sdf"
PICK_XYZ = (-1.902, -0.5, 0.074)      # pick station (arm reach)

# Verified poses
UP        = [0.0, -1.0, 0.7, 0.3]
PICK      = [0.0,  0.5, 0.3, 0.7]
LIFT      = [0.0, -0.3, 0.5, 0.5]
ROT_HIGH  = [1.1, -0.3, 0.5, 0.5]      # swing to drop side, stay high
EXTEND    = [1.1, 0.95, -0.05, 0.6]    # pose C: reach down past wheel (floor)
GOPEN, GCLOSE = 0.019, -0.006

class Seq(Node):
    def __init__(self):
        super().__init__("pick_sequencer")
        self.sub = self.create_subscription(Bool, "/start_pick_and_place", self.on_trig, 10)
        self.arm = self.create_publisher(JointTrajectory, "/arm_controller/joint_trajectory", 10)
        self.att = self.create_publisher(String, "/attach", 10)
        self.det = self.create_publisher(String, "/detach", 10)
        self.grip = ActionClient(self, GripperCommand, "/gripper_controller/gripper_cmd")
        self.spawn = self.create_client(SpawnEntity, "/spawn_entity")
        self.delete = self.create_client(DeleteEntity, "/delete_entity")
        self.go = False; self.busy = False
        self.get_logger().info("Sequencer ready. Waiting for /start_pick_and_place...")

    def on_trig(self, m):
        if m.data and not self.busy:
            self.get_logger().info("TRIGGER -> starting ordered pick-and-place")
            self.go = True

    def move(self, pos, sec):
        t = JointTrajectory(); t.joint_names = ["joint1","joint2","joint3","joint4"]
        p = JointTrajectoryPoint(); p.positions = [float(x) for x in pos]
        p.time_from_start.sec = sec; t.points = [p]
        self.arm.publish(t); time.sleep(sec + 1.5)

    def gripper(self, pos):
        g = GripperCommand.Goal(); g.command.position = float(pos); g.command.max_effort = 15.0
        self.grip.wait_for_server(); f = self.grip.send_goal_async(g)
        t0 = time.time()
        while not f.done() and time.time()-t0 < 5: time.sleep(0.1)
        time.sleep(1.0)

    def spawn_block(self, c):
        d = DeleteEntity.Request(); d.name = f"{c}_block"; self.delete.call_async(d); time.sleep(0.5)
        s = SpawnEntity.Request(); s.name = f"{c}_block"; s.xml = open(SDF.format(c)).read()
        s.initial_pose.position.x = PICK_XYZ[0]; s.initial_pose.position.y = PICK_XYZ[1]
        s.initial_pose.position.z = PICK_XYZ[2]; self.spawn.call_async(s); time.sleep(1.5)

    def pubs(self, pub, txt):
        m = String(); m.data = txt; pub.publish(m); time.sleep(1.0)

    def cycle(self, c):
        self.get_logger().info(f"=== {c.upper()} ===")
        self.move(UP, 3); self.spawn_block(c)                    # present block at pick station
        self.gripper(GOPEN); self.move(PICK, 3); self.gripper(GCLOSE)   # grip
        self.pubs(self.att, f"turtlebot3_manipulation_system::gripper_left_link {c}_block")  # attach
        self.move(LIFT, 4)                                       # lift
        self.move(ROT_HIGH, 4)                                   # swing to drop side (high)
        self.move(EXTEND, 5)                                     # reach down past wheel
        self.pubs(self.det, "release"); self.gripper(GOPEN)      # place on floor + release
        self.move(ROT_HIGH, 4); self.move(UP, 4)                 # retreat (lift, then home)
        self.get_logger().info(f"=== {c.upper()} placed on floor ===")

    def run(self):
        self.busy = True
        for c in ORDER: self.cycle(c)
        self.get_logger().info("=== ALL DONE: red, blue, green placed ===")
        self.busy = False; self.go = False

def main():
    rclpy.init(); n = Seq()
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
