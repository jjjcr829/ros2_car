import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription, DeclareLaunchArgument, TimerAction, OpaqueFunction
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def launch_setup(context, *args, **kwargs):
    pkg_ros_car = get_package_share_directory('ros_car')
    use_sim_time = LaunchConfiguration('use_sim_time').perform(context).lower() == 'true'
    standalone = LaunchConfiguration('standalone').perform(context).lower() == 'true'

    urdf_file = os.path.join(pkg_ros_car, 'urdf', 'ros_car.urdf.xacro')
    world_file = os.path.join(pkg_ros_car, 'worlds', 'fishbot.world')
    rviz_config = os.path.join(pkg_ros_car, 'config', 'rviz_config.rviz')

    spawn_x = LaunchConfiguration('spawn_x').perform(context)
    spawn_y = LaunchConfiguration('spawn_y').perform(context)

    doc = xacro.process_file(urdf_file, mappings={
        'use_sim': 'true' if use_sim_time else 'false',
    })
    robot_description = doc.toxml()

    urdf_spawn_file = '/tmp/ros_car_spawn.urdf'
    with open(urdf_spawn_file, 'w') as f:
        f.write(robot_description)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description,
                     'use_sim_time': use_sim_time}]
    )

    map_odom_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['--x', '0', '--y', '0', '--z', '0',
                   '--roll', '0', '--pitch', '0', '--yaw', '0',
                   '--frame-id', 'map', '--child-frame-id', 'odom'],
        output='screen'
    )

    actions = []

    if standalone:
        actions.append(map_odom_tf_node)

    if use_sim_time:
        joint_state_publisher_node = Node(
            package='ros_car',
            executable='sim_joint_state_publisher.py',
            name='sim_joint_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': True, 'rate': 50.0}]
        )

        rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
            parameters=[{'use_sim_time': True}],
            additional_env={'MESA_GL_VERSION_OVERRIDE': '3.3'}
        )

        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                get_package_share_directory('gazebo_ros'),
                '/launch', '/gzserver.launch.py'
            ]),
            launch_arguments={'world': world_file}.items()
        ))
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                get_package_share_directory('gazebo_ros'),
                '/launch', '/gzclient.launch.py'
            ])
        ))

        actions.append(TimerAction(
            period=2.0,
            actions=[Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=['-entity', 'ros_car', '-file', urdf_spawn_file,
                           '-x', spawn_x, '-y', spawn_y, '-z', '0.18'],
                output='screen'
            )]
        ))

        actions.append(TimerAction(
            period=4.0,
            actions=[robot_state_publisher_node,
                     joint_state_publisher_node,
                     rviz_node]
        ))
    else:
        actions.append(robot_state_publisher_node)

    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true',
                              description='Use simulation time and Gazebo (false for real car)'),
        DeclareLaunchArgument('standalone', default_value='true',
                              description='Running standalone (publish map->odom; false when included by nav/mapping)'),
        DeclareLaunchArgument('spawn_x', default_value='-0.02'),
        DeclareLaunchArgument('spawn_y', default_value='0.10'),
        OpaqueFunction(function=launch_setup),
    ])
