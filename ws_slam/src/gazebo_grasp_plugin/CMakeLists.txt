cmake_minimum_required(VERSION 3.8)
project(gazebo_grasp_plugin)

# Find the packages we depend on
find_package(ament_cmake REQUIRED)
find_package(gazebo_dev REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# Include Gazebo's header directories
include_directories(${GAZEBO_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})

# Build our plugin as a shared library (.so file that Gazebo loads)
add_library(grasp_plugin SHARED src/grasp_plugin.cpp)

# Connect (link) our plugin to the libraries it uses
ament_target_dependencies(grasp_plugin rclcpp std_msgs gazebo_ros)
target_link_libraries(grasp_plugin ${GAZEBO_LIBRARIES})

# Install the built plugin so Gazebo can find it
install(TARGETS grasp_plugin
  LIBRARY DESTINATION lib
)

ament_package()
