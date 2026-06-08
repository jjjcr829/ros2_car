import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_ros_car = get_package_share_directory('ros_car')
    use_sim_time = LaunchConfiguration('use_sim_time')

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_ros_car, '/launch', '/sim.launch.py'
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'standalone': 'false',
        }.items()
    )

    slam_config = os.path.join(pkg_ros_car, 'config', 'mapper_params.yaml')

    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_config,
            {'use_sim_time': use_sim_time}
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use simulation time and Gazebo (false for real car)'),
        sim_launch,
        slam_toolbox_node,
    ])
