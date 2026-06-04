import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_ros_car = get_package_share_directory('ros_car')
    urdf_file = os.path.join(pkg_ros_car, 'urdf', 'ros_car.urdf')
    world_file = os.path.join(pkg_ros_car, 'worlds', 'fishbot.world')
    rviz_config = os.path.join(pkg_ros_car, 'config', 'rviz_config.rviz')

    spawn_x = LaunchConfiguration('spawn_x', default='-0.02')
    spawn_y = LaunchConfiguration('spawn_y', default='0.10')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description,
                     'use_sim_time': True}]
    )

    joint_state_publisher_node = Node(
        package='ros_car',
        executable='sim_joint_state_publisher.py',
        name='sim_joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'rate': 50.0}]
    )

    map_odom_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0', '--y', '0', '--z', '0',
                   '--roll', '0', '--pitch', '0', '--yaw', '0',
                   '--frame-id', 'map', '--child-frame-id', 'odom'],
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
        parameters=[{'use_sim_time': True}],
        additional_env={'MESA_GL_VERSION_OVERRIDE': '3.3'}
    )

    return LaunchDescription([
        DeclareLaunchArgument('spawn_x', default_value='-0.02'),
        DeclareLaunchArgument('spawn_y', default_value='0.10'),

        map_odom_tf_node,

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                get_package_share_directory('gazebo_ros'),
                '/launch', '/gzserver.launch.py'
            ]),
            launch_arguments={'world': world_file}.items()
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                get_package_share_directory('gazebo_ros'),
                '/launch', '/gzclient.launch.py'
            ])
        ),

        TimerAction(
            period=2.0,
            actions=[Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=['-entity', 'ros_car', '-file', urdf_file,
                           '-x', spawn_x, '-y', spawn_y, '-z', '0.18'],
                output='screen'
            )]
        ),

        TimerAction(
            period=4.0,
            actions=[robot_state_publisher_node,
                     joint_state_publisher_node,
                     rviz_node]
        ),
    ])
