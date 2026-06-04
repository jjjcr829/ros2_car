#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class SimJointStatePublisher(Node):
    def __init__(self):
        super().__init__('sim_joint_state_publisher')
        self.declare_parameter('rate', 50.0)
        rate = self.get_parameter('rate').value
        if isinstance(rate, int):
            rate = float(rate)

        self.pub = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(1.0 / rate, self.publish)

        self.joint_names = [
            'left_front_steer_joint',
            'right_front_steer_joint',
            'left_front_roll_joint',
            'right_front_roll_joint',
            'left_rear_roll_joint',
            'right_rear_roll_joint',
        ]
        self.get_logger().info('Publishing 6 joints to /joint_states')

    def publish(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [0.0] * len(self.joint_names)
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = SimJointStatePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
