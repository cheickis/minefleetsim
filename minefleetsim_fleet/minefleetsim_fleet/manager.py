"""Odometry waypoint demo for two generic mining vehicles.

For simulation/prototyping only. Not a safety-rated traffic controller.
"""
import math
import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import String

from .logic import TunnelLease

ROBOT_NAMES = ('robot_1', 'robot_2')
# Eastbound starts west of tunnel; westbound starts east.
GOALS = {'robot_1': (5.4, 0.0), 'robot_2': (-5.4, 0.0)}
DIRECTIONS = {'robot_1': 1.0, 'robot_2': -1.0}


def clamp(x, low, high):
    return max(low, min(high, x))


def yaw_of(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


class FleetManager(Node):
    def __init__(self):
        super().__init__('fleet_manager')
        self.lease = TunnelLease()
        self.poses = {}
        self.odom_seen_at = {}
        self.done = set()
        self.released = set()
        self.last_status = None
        self.cmd = {}
        self.status_pub = self.create_publisher(String, '/minefleetsim/status', 10)
        for name in ROBOT_NAMES:
            self.cmd[name] = self.create_publisher(Twist, f'/{name}/cmd_vel', 10)
            self.create_subscription(Odometry, f'/{name}/odom',
                                     lambda msg, n=name: self.on_odom(n, msg), 10)
        self.timer = self.create_timer(0.1, self.step)
        self.get_logger().info('MineFleetSim ready; waiting for both robot odometry streams')

    def on_odom(self, name, msg):
        p = msg.pose.pose.position
        self.poses[name] = (p.x, p.y, yaw_of(msg.pose.pose.orientation))
        self.odom_seen_at[name] = time.monotonic()

    def report(self, text):
        if text != self.last_status:
            self.last_status = text
            self.get_logger().info(text)
        self.status_pub.publish(String(data=text))

    def send(self, name, v=0.0, w=0.0):
        cmd = Twist()
        cmd.linear.x = float(v)
        cmd.angular.z = float(w)
        self.cmd[name].publish(cmd)

    def step(self):
        now = time.monotonic()
        if any(n not in self.poses for n in ROBOT_NAMES):
            for n in ROBOT_NAMES:
                self.send(n)
            self.report('Waiting for both robot odometry streams')
            return
        if any(now - self.odom_seen_at[n] > 0.7 for n in ROBOT_NAMES):
            for n in ROBOT_NAMES:
                self.send(n)
            self.report('STOP: robot odometry stale (demo hold)')
            return

        for n in ROBOT_NAMES:
            x, y, yaw = self.poses[n]
            gx, gy = GOALS[n]
            dist = math.hypot(gx-x, gy-y)
            if n in self.done or dist < 0.25:
                if n not in self.done:
                    self.done.add(n)
                    if self.lease.owner == n:
                        self.lease.release(n)
                        self.released.add(n)
                self.send(n)
                continue

            if n not in self.released:
                granted = self.lease.request(n)
                if not granted:
                    self.send(n)
                    continue
            # Robot has the exclusive lease until clear of x=+/-3.5.
            if self.lease.owner == n and DIRECTIONS[n] * x > 3.5:
                self.lease.release(n)
                self.released.add(n)

            heading_error = wrap(math.atan2(gy-y, gx-x) - yaw)
            angular = clamp(2.0 * heading_error, -0.7, 0.7)
            speed = min(0.65, 0.8 * dist) if abs(heading_error) < 0.4 else 0.0
            self.send(n, speed, angular)

        self.report('Completed: both vehicles crossed safely' if len(self.done) == 2
                    else f'Tunnel owner: {self.lease.owner or "free"}; '
                         f'waiting: {",".join(self.lease.queue) or "none"}; '
                         f'completed: {len(self.done)}/2')

    def shutdown(self):
        for n in ROBOT_NAMES:
            self.send(n)


def main(args=None):
    rclpy.init(args=args)
    node = FleetManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.shutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
