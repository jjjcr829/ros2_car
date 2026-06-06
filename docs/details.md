# JCR ROS 2 Car 详细文档

## 工作空间结构

```text
ros2_car/
├── src/
│   ├── ros_car/              # 主包：阿克曼小车（稳定，推荐使用）
│   │   ├── config/
│   │   │   ├── mapper_params.yaml      # SLAM Toolbox 参数
│   │   │   ├── nav2_params.yaml        # Nav2 导航参数（317 行）
│   │   │   └── rviz_config.rviz        # RViz2 布局
│   │   ├── launch/
│   │   │   ├── sim.launch.py           # 仿真启动（含 Gazebo）
│   │   │   ├── mapping.launch.py       # 建图启动
│   │   │   └── nav.launch.py           # 导航启动
│   │   ├── maps/
│   │   │   ├── map6.yaml / map6.pgm    # 预存地图
│   │   │   └── my_map3.yaml
│   │   ├── scripts/
│   │   │   ├── sim_joint_state_publisher.py  # 关节状态占位（仿真用）
│   │   │   ├── tf_publisher.py               # URDF TF 发布（备用）
│   │   │   ├── save_map.sh                   # 地图保存脚本
│   │   │   ├── start_mapping.sh              # 建图启动脚本
│   │   │   └── teleop.sh                     # 键盘控制脚本
│   │   ├── urdf/
│   │   │   └── ros_car.urdf.xacro    # 机器人模型（含条件编译）
│   │   └── worlds/
│   │       ├── fishbot.world          # 六边形竞技场（默认）
│   │       ├── fish.world             # 大型迷宫
│   │       └── simple_obstacles.world # 简单障碍
│   └── car_demo1/          # 实验包：差速小车（有已知 bug）
├── docs/
├── AGENTS.md
└── README.md
```

## 包说明

| 包名 | 路径 | 类型 | 作用 |
|------|------|------|------|
| `ros_car` | `src/ros_car` | `ament_cmake` | 阿克曼小车仿真/导航（核心包） |
| `car_demo1` | `src/car_demo1` | `ament_cmake` | 差速小车实验（有语法错误，仅供参考） |

## 启动架构

### 参数传递链

所有启动文件通过 `use_sim_time` 参数串联，一条参数控制仿真/实车切换：

```
ros2 launch ros_car nav.launch.py use_sim_time:=false
    │
    ├── nav.launch.py
    │   ├── DeclareLaunchArgument('use_sim_time')  ← 接收 'false'
    │   ├── IncludeLaunchDescription(sim.launch.py, use_sim_time='false', standalone='false')
    │   └── Nav2 节点（amcl/controller/planner/...）use_sim_time = false
    │
    └── sim.launch.py（被包含）
        ├── use_sim_time=false → 跳过 Gazebo/spawn/RViz
        ├── standalone=false → 不发布 map→odom（由 AMCL 提供）
        ├── URDF xacro use_sim=false → 裁剪所有 <gazebo> 块
        └── robot_state_publisher use_sim_time=false → 系统时钟
```

### 启动模式总结

| 模式 | 命令 | Gazebo | map→odom 来源 | 时钟 |
|------|------|--------|---------------|------|
| 纯仿真 | `ros2 launch ros_car sim.launch.py` | ✓ | static TF | 仿真 |
| 建图 | `ros2 launch ros_car mapping.launch.py` | ✓ | SLAM Toolbox | 仿真 |
| 导航 | `ros2 launch ros_car nav.launch.py map:=...` | ✓ | AMCL | 仿真 |
| 实车 | `... use_sim_time:=false` | ✗ | AMCL 或实车里程计 | 系统 |

## 话题与坐标系

### 主要话题

**Gazebo 仿真模式：**

| 话题 | 类型 | 方向 | 来源 |
|------|------|------|------|
| `/cmd_vel` | `geometry_msgs/Twist` | 订阅 | 键盘/导航节点 → 阿克曼插件 |
| `/scan` | `sensor_msgs/LaserScan` | 发布 | Gazebo 激光插件 |
| `/imu` | `sensor_msgs/Imu` | 发布 | Gazebo IMU 插件 |
| `/odom` | `nav_msgs/Odometry` | 发布 | 阿克曼驱动插件 |
| `/joint_states` | `sensor_msgs/JointState` | 发布 | sim_joint_state_publisher（零位占位） |
| `/tf` | `tf2_msgs/TFMessage` | 发布 | 多节点 |
| `/map` | `nav_msgs/OccupancyGrid` | 发布 | SLAM Toolbox / map_server |

### TF 坐标系链

```
map → odom → base_link
               ├── laser_support → laser_link
               ├── imu_link
               ├── left_front_knuckle_link → left_front_link
               ├── right_front_knuckle_link → right_front_link
               ├── left_rear_link
               └── right_rear_link
```

- `map → odom`：由 SLAM Toolbox（建图）或 AMCL（导航）或 static_transform_publisher（纯仿真）发布
- `odom → base_link`：由 Gazebo 阿克曼驱动插件发布
- `base_link → 各传感器/车轮`：由 `robot_state_publisher` 根据 URDF 发布

## 关键配置

### URDF 模型

- 文件：`src/ros_car/urdf/ros_car.urdf.xacro`
- 使用 xacro 条件编译，通过 `use_sim` 属性控制是否包含 Gazebo 插件
- 底盘尺寸：0.32 × 0.20 × 0.08m，质量 2.0kg
- 轴距：0.17m，轮距：0.28m，轮半径：0.05m
- 最大转向角：±0.7rad，最大速度：2.0 m/s

### SLAM 参数

- 文件：`src/ros_car/config/mapper_params.yaml`
- `odom_frame: odom`，`map_frame: map`，`base_frame: base_link`
- `scan_topic: /scan`，`mode: mapping`
- `map_update_interval: 5.0`，`resolution: 0.05`

### 导航参数

- 文件：`src/ros_car/config/nav2_params.yaml`
- 全局规划器：`SmacPlannerHybrid`（Reeds-Shepp 运动模型，支持倒车）
- 局部控制器：`RegulatedPurePursuit`（目标速度 0.5 m/s）
- 定位：AMCL（似然域模型，粒子数 500-2000）
- 最小转弯半径：0.22m

### Gazebo 世界文件

| 文件 | 说明 |
|------|------|
| `fishbot.world` | 默认世界，SDF 1.7，六边形竞技场含障碍 |
| `fish.world` | SDF 1.7，大型迷宫 |
| `simple_obstacles.world` | SDF 1.6，3 个方块障碍 |

所有世界文件已添加 `libgazebo_ros_factory.so` 插件，确保 `/spawn_entity` 服务可用。

## 常见故障排查

### Gazebo 打不开 / 启动闪退

```bash
# 检查 Gazebo 安装
gazebo --version
# 如报错，安装 Gazebo
sudo apt install ros-humble-gazebo-ros-pkgs
```

### /spawn_entity 服务不可用

已修复：所有 world 文件均包含 `gazebo_ros_factory` 插件。如果问题仍存在：

```bash
ros2 service list | grep spawn
```

### 无 /scan 数据

```bash
# 检查话题
ros2 topic list | grep scan
ros2 topic echo /scan --once
# 确认 Gazebo 激光插件已加载（查看 gzserver 日志）
```

### 无 /odom 数据

阿克曼驱动插件未加载。确认：
1. URDF xacro 编译后包含 `<gazebo>` 插件块（`use_sim=true` 时应有）
2. `colcon build` 重新编译后启动

### TF 树断裂

```bash
ros2 run tf2_tools view_frames
# 检查 map → odom → base_link 链路
```

### map→odom 双发布

`sim.launch.py` 被包含时自动设置 `standalone=false`，不再发布 map→odom。如直接运行 `sim.launch.py` 建图请用 `mapping.launch.py`。

### WSL 特有：RViz 不显示

`sim.launch.py` 默认设置 `MESA_GL_VERSION_OVERRIDE=3.3`。如在原生 Linux 运行，移除该环境变量。

### 构建失败

```bash
# 删除旧构建产物重试
rm -rf build/ install/ log/
colcon build --packages-select ros_car
```
