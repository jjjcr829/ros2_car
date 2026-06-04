import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    package_name = 'car_demo1'
    
    pkg_path = get_package_share_directory(package_name)
    xacro_file = os.path.join(pkg_path, 'urdf', 'car.urdf.xacro')
    robot_description_raw = xacro.process_file(xacro_file).toxml()
    
    # 机器人状态发布节点
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw, 'use_sim_time': True}]
    )
    
    # 启动新版 Gazebo
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', '/tmp/obstacle_world.sdf'],cmd=['ign', 'gazebo', '/tmp/obstacle_world.sdf'],
        output='screen'
    )
    
    # 生成小车（使用新版 Gazebo 命令）
    spawn_entity = ExecuteProcess(
        cmd=['bash', '-c', f'xacro {xacro_file} > /tmp/car.urdf && ign service -s /world/empty/create --reqtype ignition.msgs.EntityFactory --reptype ignition.msgs.Boolean --timeout 1000 --req \'sdf_filename: "/tmp/car.urdf", name: "box_car"\''],
        output='screen'
    )
    
    # 键盘控制节点
    teleop_keyboard = ExecuteProcess(
        cmd=['xterm', '-e', 'ros2 run teleop_twist_keyboard teleop_twist_keyboard'],
        shell=True,
        output='screen'
    )
    
    # Slam Toolbox 建图节点
    slam_toolbox = Node(
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
    )
    
    # 启动 RViz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        TimerAction(period=5.0, actions=[spawn_entity]),
        teleop_keyboard,
        slam_toolbox,
        rviz
    ])
