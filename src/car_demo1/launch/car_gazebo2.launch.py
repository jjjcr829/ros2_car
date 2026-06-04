import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    package_name = 'car_demo1'
    
    pkg_share = get_package_share_directory(package_name)
    
    xacro_path = os.path.join(pkg_share, 'urdf/car.urdf.xacro')
    urdf_path = '/tmp/car.urdf'
    world_path = os.path.join(pkg_share, 'worlds/room.world')
    
    # 1. 转换 xacro 到 urdf
    xacro_cmd = ExecuteProcess(
        cmd=['xacro', xacro_path, '-o', urdf_path],
        shell=True
    )
    
    # 2. 启动 Gazebo（带 ROS 插件）
    gazebo_cmd = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', 
             '-s', 'libgazebo_ros_factory.so', world_path],
        output='screen'
    )
    
    # 3. 等待 Gazebo 启动后生成机器人
    spawn_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'car', '-file', urdf_path, 
                   '-x', '0', '-y', '0', '-z', '0.1'],
        output='screen'
    )
    
    # 延迟 5 秒后执行 spawn（确保 Gazebo 完全启动）
    delayed_spawn_cmd = TimerAction(period=5.0, actions=[spawn_cmd])
    
    # 4. robot_state_publisher
    robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        arguments=[urdf_path],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )
    
    # 5. joint_state_publisher
    joint_state_publisher_cmd = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        arguments=[urdf_path],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )
    
    # 6. RViz2（可选，如果不想自动启动可以注释掉）
    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )
    
    return LaunchDescription([
        xacro_cmd,
        gazebo_cmd,
        delayed_spawn_cmd,  # 延迟生成小车
        robot_state_publisher_cmd,
        joint_state_publisher_cmd,
        rviz_cmd,
    ])