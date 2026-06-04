import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 启动新版 Gazebo
        ExecuteProcess(
            cmd=['ign', 'gazebo', 'empty.sdf'],
            output='screen'
        ),
        
        # 等待5秒后生成小车
        TimerAction(
            period=5.0,
            actions=[
                ExecuteProcess(
                    cmd=['bash', '-c', 'cd ~/ros2_ws/src/car_demo1 && xacro urdf/car.urdf.xacro > /tmp/car.urdf && ign service -s /world/empty/create --reqtype ignition.msgs.EntityFactory --reptype ignition.msgs.Boolean --timeout 1000 --req \'sdf_filename: "/tmp/car.urdf", name: "box_car"\''],
                    output='screen'
                )
            ]
        ),
        
        # 启动桥接（使用配置文件）
        TimerAction(
            period=8.0,
            actions=[
                Node(
                    package='ros_gz_bridge',
                    executable='parameter_bridge',
                    arguments=['--config-file', os.path.expanduser('~/ros2_ws/src/car_demo1/config/bridge.yaml')],
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
        
        # SLAM Toolbox
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
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
        ),
        
        # RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )
    ])
