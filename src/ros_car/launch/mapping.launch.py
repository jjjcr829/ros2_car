import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_ros_car = get_package_share_directory('ros_car')

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_ros_car, '/launch', '/sim.launch.py'
        ])
    )

    slam_config = os.path.join(pkg_ros_car, 'config', 'mapper_params.yaml')

    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_config,
            {'use_sim_time': True}
        ]
    )

    return LaunchDescription([
        sim_launch,
        slam_toolbox_node,
    ])
