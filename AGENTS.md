# AGENTS.md — ros2_car

## Workspace layout

- ROS2 workspace with two colcon packages under `src/`.
- **`ros_car`** — stable Ackermann car (classic Gazebo). This is the working package per README.
- **`car_demo1`** — experimental differential-drive car (Ignition Gazebo + xacro). Has bugs; expect breakage.

## Build

```bash
source /opt/ros/<distro>/setup.bash
colcon build
source install/setup.bash
```

## Launch (ros_car only — the working package)

| Mode | Command |
|------|---------|
| Sim only | `ros2 launch ros_car sim.launch.py` |
| Sim + SLAM | `ros2 launch ros_car mapping.launch.py` |
| Full Nav2 stack | `ros2 launch ros_car nav.launch.py` |
| Real car (no Gazebo) | `ros2 launch ros_car sim.launch.py use_sim_time:=false` |

All launches accept `use_sim_time:=true|false` to toggle between Gazebo simulation and real hardware. This single parameter also controls `use_sim_time` (all nodes). The URDF xacro strips all `<gazebo>` blocks when `use_sim_time:=false`.

## Gotchas

- **`ros_car` uses classic Gazebo** (`gzserver`/`gzclient`); `car_demo1` uses Ignition (`ign gazebo` + `ros_gz_bridge`).
- **`nav.launch.py` defaults to `map6.yaml`.** Override with `map:=` for other maps.
- **`car_gazebo.launch.py` (car_demo1) has a syntax error** — line 26 has a duplicate `cmd=` argument. The file won't parse.
- **`MESA_GL_VERSION_OVERRIDE: '3.3'`** is set on the RViz node in `sim.launch.py`. This is a WSL GPU workaround; remove if running natively on Linux.
- **`ros_car` uses xacro to process URDF at launch time.** Edit `src/ros_car/urdf/ros_car.urdf.xacro` directly. All `<gazebo>` blocks are wrapped with `<xacro:if value="${use_sim}">` and are excluded when `use_sim_time:=false`.
- **Custom Python scripts** in `src/ros_car/scripts/` are installed as PROGRAMS by CMakeLists.txt. After editing them, rebuild with `colcon build` to pick up changes.
- **The `sim_joint_state_publisher.py` node publishes 6 joints as zeros** at `/joint_states` — it exists to satisfy `robot_state_publisher` TF tree requirements; real joint states come from the Gazebo Ackermann plugin (topic `/{namespace}/joint_states`).

## Dependencies

- `ros_car` requires: `gazebo_ros`, SLAM Toolbox, Nav2, `teleop_twist_keyboard`, `rviz2`, `xacro`
- `car_demo1` additionally requires: `xacro`, `ros_gz_bridge`, Ignition Gazebo
- No test dependencies are actually used (tests exist only as stubs in `package.xml`).

## World files

- `ros_car` sim defaults to `fishbot.world` (SDF 1.7, hex arena with obstacles).
- `fish.world` is a larger maze (SDF 1.7).
- `car_demo1` worlds are SDF 1.6.

## Other resources

- Full documentation at `docs/details.md` — workspace structure, topics, frames, troubleshooting.
- README.md has quick-start commands.

## No CI, no tests, no linting

There is no CI pipeline, no pre-commit config, and no test suite. Adding lint/test infrastructure would start from scratch.
