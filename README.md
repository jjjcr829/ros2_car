# JCR ROS 2 Car

## 项目简介

基于 ROS 2 Humble + Gazebo Classic 的阿克曼转向小车仿真与导航平台。

### 核心功能

- 🚗 **阿克曼底盘仿真**：四轮阿克曼转向，Gazebo Ackermann 驱动插件，支持前进/倒车
- 📡 **激光雷达感知**：360 线激光仿真，20Hz，0.1-8m 范围，高斯噪声模拟
- 🗺️ **SLAM 同步建图**：基于 SLAM Toolbox 异步建图，支持回环检测
- 🧭 **自主导航**：SmacPlannerHybrid（Reeds-Shepp）全局规划 + RegulatedPurePursuit 局部控制，阿克曼运动学约束

## 项目文档

- [详细文档](docs/details.md) — 工作空间结构、包说明、话题与坐标系、关键配置、常见故障排查
- [fix 分支修改记录](docs/changes.md) — 基于 master 的全部修改说明

## 快速开始

### 环境要求

#### 操作系统

| 环境 | 说明 |
|------|------|
| Ubuntu 22.04 | 推荐，直接运行 Gazebo + RViz |

#### 软件

| 组件 | 版本 | 验证命令 |
|------|------|----------|
| ROS 2 | Humble | `printenv ROS_DISTRO` |
| Gazebo | Classic 11.x | `gazebo --version` |
| 构建工具 | colcon | `colcon --version` |
| Python | 3.10 | `python3 --version` |

#### 安装 ROS 2

```bash
# 推荐使用鱼香 ROS 一键安装
wget http://fishros.com/install -O fishros && bash fishros
```

验证安装：

```bash
source /opt/ros/humble/setup.bash
ros2 run demo_nodes_cpp talker
```

### 安装依赖

```bash
# 系统依赖
sudo apt update && sudo apt install -y \
  python3-colcon-common-extensions python3-rosdep

# ROS 包依赖
sudo apt install -y \
  ros-humble-gazebo-ros \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-slam-toolbox \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-teleop-twist-keyboard \
  ros-humble-rviz2 \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-tf2-tools
```

### 获取源码

```bash
cd ~
git clone https://github.com/jjjcr829/ros2_car.git
```

### 构建与环境加载

```bash
cd ~/ros2_car
source /opt/ros/humble/setup.bash
colcon build --packages-select ros_car
source install/setup.bash
```

可选：写入 `~/.bashrc`。

```bash
echo "source ~/ros2_car/install/setup.bash" >> ~/.bashrc
```

## 启动

### 仿真启动

```bash
ros2 launch ros_car sim.launch.py
```

### SLAM 建图

```bash
# 启动建图
ros2 launch ros_car mapping.launch.py

# 键盘控制
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 保存地图
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

### 导航启动

```bash
ros2 launch ros_car nav.launch.py map:=src/ros_car/maps/map6.yaml
```

## 命令速查

```bash
# 进入工作空间
cd ~/ros2_car

# 加载 ROS 环境
source /opt/ros/humble/setup.bash

# 构建
colcon build --packages-select ros_car
source install/setup.bash

# 仿真
ros2 launch ros_car sim.launch.py

# 建图
ros2 launch ros_car mapping.launch.py

# 导航（默认加载 src/ros_car/maps/map6.yaml）
ros2 launch ros_car nav.launch.py

# 键盘控制
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 保存地图
ros2 run nav2_map_server map_saver_cli -f ~/my_map

# 调试命令
ros2 node list
ros2 topic list
ros2 topic echo /scan
ros2 topic echo /odom
ros2 topic echo /cmd_vel
ros2 run tf2_tools view_frames
```
