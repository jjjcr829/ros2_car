import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, OpaqueFunction
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    pkg_ros_car = get_package_share_directory('ros_car')
    use_sim_time = LaunchConfiguration('use_sim_time').perform(context).lower() == 'true'

    map_file = LaunchConfiguration('map').perform(context)
    nav2_param = LaunchConfiguration('nav2_param').perform(context)

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            pkg_ros_car, '/launch', '/sim.launch.py'
        ]),
        launch_arguments={
            'use_sim_time': str(use_sim_time).lower(),
            'standalone': 'false',
        }.items()
    )

    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'yaml_filename': map_file}]
    )

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[nav2_param,
                    {'use_sim_time': use_sim_time}]
    )

    lifecycle_manager_localization = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'bond_timeout': 30.0,
                     'attempt_respawn_reconnection': True,
                     'node_names': ['map_server', 'amcl']}]
    )

    controller_server_node = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_param,
                    {'use_sim_time': use_sim_time}]
    )

    planner_server_node = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_param,
                    {'use_sim_time': use_sim_time}]
    )

    behavior_server_node = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[nav2_param,
                    {'use_sim_time': use_sim_time}]
    )

    bt_navigator_node = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[nav2_param,
                    {'use_sim_time': use_sim_time}]
    )

    smoother_server_node = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        parameters=[nav2_param,
                    {'use_sim_time': use_sim_time}]
    )

    lifecycle_manager_navigation = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'bond_timeout': 30.0,
                     'attempt_respawn_reconnection': True,
                     'node_names': ['controller_server',
                                    'planner_server',
                                    'behavior_server',
                                    'bt_navigator',
                                    'smoother_server']}]
    )

    return [
        sim_launch,
        TimerAction(period=15.0, actions=[
            map_server_node,
            amcl_node,
            lifecycle_manager_localization,
            controller_server_node,
            planner_server_node,
            behavior_server_node,
            bt_navigator_node,
            smoother_server_node,
            lifecycle_manager_navigation,
        ]),
    ]


def generate_launch_description():
    pkg_ros_car = get_package_share_directory('ros_car')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use simulation time and Gazebo (false for real car)'),
        DeclareLaunchArgument('map',
                              default_value=os.path.join(pkg_ros_car, 'maps', 'map6.yaml'),
                              description='Full path to map yaml file to load'),
        DeclareLaunchArgument('nav2_param',
                              default_value=os.path.join(pkg_ros_car, 'config', 'nav2_params.yaml'),
                              description='Full path to Nav2 params yaml'),
        OpaqueFunction(function=launch_setup),
    ])
