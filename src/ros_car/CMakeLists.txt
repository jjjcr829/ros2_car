cmake_minimum_required(VERSION 3.8)
project(ros_car)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf worlds launch config maps scripts
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

install(PROGRAMS scripts/sim_joint_state_publisher.py scripts/tf_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()