import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    urdf_file = os.path.expanduser('~/ros2_ws/src/car_demo1/urdf/car.urdf.xacro')
    
    return LaunchDescription([
        # 启动新版 Gazebo (Ignition)
        ExecuteProcess(
            cmd=['ign', 'gazebo', 'empty.sdf'],
            output='screen'
        ),
        
        # 等待5秒后生成小车
        TimerAction(
            period=5.0,
            actions=[
                ExecuteProcess(
                    cmd=['bash', '-c', f'xacro {urdf_file} > /tmp/car.urdf && ign service -s /world/empty/create --reqtype ignition.msgs.EntityFactory --reptype ignition.msgs.Boolean --timeout 1000 --req \'sdf_filename: "/tmp/car.urdf", name: "box_car"\''],
                    output='screen'
                )
            ]
        ),
        
        # 等待小车生成后启动桥接
        TimerAction(
            period=8.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge', '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist'],
                    output='screen'
                )
            ]
        ),
        
        # 键盘控制
        ExecuteProcess(
            cmd=['xterm', '-e', 'ros2 run teleop_twist_keyboard teleop_twist_keyboard'],
            shell=True,
            output='screen'
        ),
        
        # RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{'use_sim_time': True}]
        ),
        
        # SLAM Toolbox (可选)
        Node(
            package='slam_toolbox',
            executable='sync_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'base_frame': 'base_footprint',
                'odom_frame': 'odom',
                'map_frame': 'map',
                'scan_topic': '/scan',
                'mode': 'mapping'
            }]
        )
    ])
