import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    urdf_file = os.path.expanduser('~/ros2_ws/src/car_demo1/urdf/car.urdf.xacro')
    
    # 创建带障碍物的世界文件
    world_file = '/tmp/simple_obstacle.sdf'
    if not os.path.exists(world_file):
        with open(world_file, 'w') as f:
            f.write('''<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="default">
    <model name="ground">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>20 20</size></plane></geometry>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>20 20</size></plane></geometry>
          <material><ambient>0.3 0.3 0.3 1</ambient></material>
        </visual>
      </link>
    </model>
    <model name="obstacle_1">
      <static>true</static>
      <pose>2.0 1.0 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision"><geometry><box><size>1.0 1.0 1.0</size></box></geometry></collision>
        <visual name="visual"><geometry><box><size>1.0 1.0 1.0</size></box></geometry><material><ambient>0.8 0.2 0.2 1</ambient></material></visual>
      </link>
    </model>
    <model name="obstacle_2">
      <static>true</static>
      <pose>-1.5 -1.5 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision"><geometry><box><size>1.0 1.0 1.0</size></box></geometry></collision>
        <visual name="visual"><geometry><box><size>1.0 1.0 1.0</size></box></geometry><material><ambient>0.2 0.2 0.8 1</ambient></material></visual>
      </link>
    </model>
    <model name="obstacle_3">
      <static>true</static>
      <pose>-1.0 2.5 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision"><geometry><box><size>0.8 0.8 0.8</size></box></geometry></collision>
        <visual name="visual"><geometry><box><size>0.8 0.8 0.8</size></box></geometry><material><ambient>0.2 0.8 0.2 1</ambient></material></visual>
      </link>
    </model>
  </world>
</sdf>''')
    
    return LaunchDescription([
        # 1. 启动 Gazebo
        ExecuteProcess(
            cmd=['ign', 'gazebo', world_file],
            output='screen'
        ),
        
        # 2. 生成小车（等待 Gazebo 启动）
        TimerAction(
            period=8.0,
            actions=[
                ExecuteProcess(
                    cmd=['bash', '-c', f'xacro {urdf_file} > /tmp/car.urdf && ign service -s /world/default/create --reqtype ignition.msgs.EntityFactory --reptype ignition.msgs.Boolean --timeout 1000 --req \'sdf_filename: "/tmp/car.urdf", name: "box_car"\''],
                    output='screen'
                )
            ]
        ),
        
        # 3. robot_state_publisher（发布 TF）
        TimerAction(
            period=10.0,
            actions=[
                Node(
                    package='robot_state_publisher',
                    executable='robot_state_publisher',
                    output='screen',
                    parameters=[{'use_sim_time': True, 'robot_description': open(urdf_file).read()}]
                )
            ]
        ),
        
        # 4. 桥接速度 (ROS → Gazebo)
        TimerAction(
            period=12.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge', '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist'],
                    output='screen'
                )
            ]
        ),
        
        # 5. 桥接雷达 (Gazebo → ROS) - 注意用的是 [
        TimerAction(
            period=12.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge', '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan'],
                    output='screen'
                )
            ]
        ),
        
        # 6. 键盘控制
        TimerAction(
            period=12.0,
            actions=[
                ExecuteProcess(
                    cmd=['xterm', '-e', 'ros2 run teleop_twist_keyboard teleop_twist_keyboard'],
                    shell=True,
                    output='screen'
                )
            ]
        ),
        
        # 7. SLAM Toolbox
        TimerAction(
            period=13.0,
            actions=[
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
                )
            ]
        ),
        
        # 8. RViz2
        TimerAction(
            period=13.0,
            actions=[
                Node(
                    package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    output='screen',
                    parameters=[{'use_sim_time': True}]
                )
            ]
        ),
    ])