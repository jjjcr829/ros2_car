from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        TimerAction(
            period=8.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge', 
                         '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist'],
                    output='screen'
                )
            ]
        ),
        TimerAction(
            period=9.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge', 
                         '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan'],
                    output='screen'
                )
            ]
        ),
    ])
