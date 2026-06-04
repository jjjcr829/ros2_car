# 倒车测试
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: -0.5}, angular: {z: 0.0}}"
