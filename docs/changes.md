# fix 分支修改记录

基于 `main`，12 文件变更，涵盖启动重构、模型改造、bug 修复和文档完善。

## 1. URDF 改为 xacro 条件编译

`src/ros_car/urdf/ros_car.urdf.xacro`、`package.xml`、`scripts/tf_publisher.py`

- 原 `ros_car.urdf`（375 行纯 URDF）重命名为 `.xacro`
- 使用 `<xacro:if value="${use_sim}">` 包裹 5 处 `<gazebo>` 块（底盘摩擦、激光、IMU、车轮摩擦、阿克曼驱动）
- `use_sim=false` 时所有 Gazebo 插件从 URDF 中裁剪
- `package.xml` 添加 `xacro` 依赖，`tf_publisher.py` 支持 `.xacro` 解析

## 2. 世界文件修复

`worlds/fishbot.world`、`fish.world`、`simple_obstacles.world`

- 3 个世界文件均添加 `<plugin name="gazebo_ros_factory" filename="libgazebo_ros_factory.so"/>`

## 3. 启动文件重构

`launch/sim.launch.py`、`launch/mapping.launch.py`、`launch/nav.launch.py`

**统一参数**
- 统一使用 `use_sim_time` 控制仿真/实车切换

**OpaqueFunction 模式**
- `sim.launch.py`：xacro 编译 → 写入 `/tmp/ros_car_spawn.urdf` → 传给 `spawn_entity.py`（避免直接传 `.xacro` 给 Gazebo）
- `nav.launch.py`：节点创建前解析所有参数，确保 `use_sim_time` 正确覆盖 YAML 硬编码值

**standalone 参数**
- `sim.launch.py` 新增 `standalone` 参数（默认 `true`），被 mapping/nav 包含时自动传 `false`
- `standalone=false` 时不发布 `map→odom` 静态 TF，避免与 SLAM/AMCL 双发布

**Nav2 参数覆盖**
- YAML 中写死的 `use_sim_time: true` 由 launch 动态覆盖

## 4. 文档完善

**新增**
- `README.md` — 项目简介、环境要求、安装指引、启动命令、命令速查
- `docs/details.md` — 工作空间结构、启动架构、话题/TF、关键配置、故障排查
- `docs/changes.md` — 本文件
- `AGENTS.md` — 项目结构、启动命令、关键注意事项

