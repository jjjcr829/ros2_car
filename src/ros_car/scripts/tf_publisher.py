#!/usr/bin/env python3
"""
Publish all TF transforms directly from URDF.
Publishes /tf for all joints (both fixed and movable) and /robot_description for RViz.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, HistoryPolicy
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import String
from tf2_ros import TransformBroadcaster
import xml.etree.ElementTree as ET
import math


def parse_origin(elem):
    xyz = [0.0, 0.0, 0.0]
    rpy = [0.0, 0.0, 0.0]
    origin = elem.find('origin')
    if origin is not None:
        if 'xyz' in origin.attrib:
            xyz = [float(v) for v in origin.attrib['xyz'].split()]
        if 'rpy' in origin.attrib:
            rpy = [float(v) for v in origin.attrib['rpy'].split()]
    return xyz, rpy


def rpy_to_quat(r, p, y):
    cr = math.cos(r * 0.5)
    sr = math.sin(r * 0.5)
    cp = math.cos(p * 0.5)
    sp = math.sin(p * 0.5)
    cy = math.cos(y * 0.5)
    sy = math.sin(y * 0.5)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def axis_angle_to_quat(ax, ay, az, angle):
    norm = math.sqrt(ax * ax + ay * ay + az * az)
    if norm < 1e-10:
        return (0.0, 0.0, 0.0, 1.0)
    ax, ay, az = ax / norm, ay / norm, az / norm
    s = math.sin(angle / 2.0)
    return (ax * s, ay * s, az * s, math.cos(angle / 2.0))


def make_transform(parent, child, xyz, rpy_quat):
    t = TransformStamped()
    t.header.frame_id = parent
    t.child_frame_id = child
    t.transform.translation.x = xyz[0]
    t.transform.translation.y = xyz[1]
    t.transform.translation.z = xyz[2]
    if len(rpy_quat) == 4:
        t.transform.rotation.x = rpy_quat[0]
        t.transform.rotation.y = rpy_quat[1]
        t.transform.rotation.z = rpy_quat[2]
        t.transform.rotation.w = rpy_quat[3]
    else:
        q = rpy_to_quat(rpy_quat[0], rpy_quat[1], rpy_quat[2])
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
    return t


class URDFTfPublisher(Node):
    def __init__(self):
        super().__init__('urdf_tf_publisher')
        self.declare_parameter('urdf_file', '')
        urdf_file = self.get_parameter('urdf_file').value
        if not urdf_file:
            self.get_logger().error('urdf_file parameter not set')
            return

        with open(urdf_file, 'r') as f:
            urdf_content = f.read()

        # Publish robot_description for RViz RobotModel
        qos = QoSProfile(depth=1,
                         durability=DurabilityPolicy.TRANSIENT_LOCAL,
                         history=HistoryPolicy.KEEP_LAST)
        self.desc_pub = self.create_publisher(String, '/robot_description', qos)
        msg = String()
        msg.data = urdf_content
        self.desc_pub.publish(msg)
        self.get_logger().info('Published /robot_description')

        self.tf_broadcaster = TransformBroadcaster(self)

        tree = ET.parse(urdf_file)
        root = tree.getroot()

        self.fixed_joints = []
        self.movable_joints = []

        all_joints = root.findall('joint')
        for joint in all_joints:
            jname = joint.get('name')
            jtype = joint.get('type', 'fixed')
            parent = joint.find('parent').get('link')
            child = joint.find('child').get('link')
            xyz, rpy = parse_origin(joint)
            axis = joint.find('axis')

            info = {
                'name': jname,
                'parent': parent,
                'child': child,
                'xyz': xyz,
                'rpy': rpy,
            }

            if jtype == 'fixed':
                self.fixed_joints.append(info)
            else:
                ax = [0.0, 0.0, 1.0]
                if axis is not None and 'xyz' in axis.attrib:
                    ax = [float(v) for v in axis.attrib['xyz'].split()]
                info['axis'] = ax
                self.movable_joints.append(info)

        self.get_logger().info(f'Fixed joints: {len(self.fixed_joints)}, '
                               f'Movable joints: {len(self.movable_joints)}')
        for j in self.movable_joints:
            self.get_logger().info(f'  [{j["name"]}] {j["parent"]} -> {j["child"]} '
                                   f'@ ({j["xyz"][0]}, {j["xyz"][1]}, {j["xyz"][2]})')

        # Publish all transforms at 50Hz (both fixed and movable)
        self.timer = self.create_timer(1.0 / 50.0, self.publish_all)

    def publish_all(self):
        now = self.get_clock().now().to_msg()
        transforms = []

        # Fixed joints
        for joint in self.fixed_joints:
            t = make_transform(joint['parent'], joint['child'],
                               joint['xyz'], joint['rpy'])
            t.header.stamp = now
            transforms.append(t)

        # Movable joints (position = 0 for all)
        for joint in self.movable_joints:
            t = TransformStamped()
            t.header.stamp = now
            t.header.frame_id = joint['parent']
            t.child_frame_id = joint['child']
            t.transform.translation.x = joint['xyz'][0]
            t.transform.translation.y = joint['xyz'][1]
            t.transform.translation.z = joint['xyz'][2]
            q = axis_angle_to_quat(
                joint['axis'][0], joint['axis'][1], joint['axis'][2], 0.0)
            t.transform.rotation.x = q[0]
            t.transform.rotation.y = q[1]
            t.transform.rotation.z = q[2]
            t.transform.rotation.w = q[3]
            transforms.append(t)

        self.tf_broadcaster.sendTransform(transforms)


def main():
    rclpy.init()
    node = URDFTfPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
