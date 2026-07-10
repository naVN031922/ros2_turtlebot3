# Base image
ARG from=ubuntu:22.04
FROM ${from}

LABEL maintainer="Cesar Gutierrez <cesar.gutierrez-marino@stud.th-deg.de>"

# Timezone Configuration
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV DEBIAN_FRONTEND=noninteractive

# Local install (en_US.UTF-8 locale)
RUN apt update && apt install -y locales \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
    && export LANG=en_US.UTF-8

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    python3 \
    python3-pip \
    libssl-dev \
    libncurses5-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    uuid-dev \
    zlib1g-dev \
    lsb-release \
    gedit \
    nano \
    unzip \
    gnupg2

# Install ROS 2 Humble and setup repositories correctly
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - \
    && echo "deb [arch=amd64] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2-latest.list \
    && apt-get update \
    && apt-get install -y \
    ros-humble-desktop \
    ros-humble-ros-base \
    python3-argcomplete \
    python3-pip \
    python3-pytest-cov \
    python3-flake8 \
    python3-rosdep \
    python3-setuptools \
    libbullet-dev \
    python3-vcstool \
    python3-colcon-mixin \
    python3-colcon-common-extensions

# Configure colcon mixin
RUN colcon mixin add default https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml && colcon mixin update default

# Installing Python3 components 
RUN python3 -m pip install -U \
    argcomplete \
    flake8-blind-except \
    flake8-builtins \
    flake8-class-newline \
    flake8-comprehensions \
    flake8-deprecated \
    flake8-docstrings \
    flake8-import-order \
    flake8-quotes \
    pytest-repeat \
    pytest-rerunfailures \
    pytest
    
RUN apt-get install -y \
	g++ \
	clang \
	clang-format \
	libboost-all-dev \
	libeigen3-dev \
	libyaml-cpp-dev \
	libopencv-dev \
	libasio-dev \
	libtinyxml2-dev \
	qtbase5-dev \
	python3-empy \
	python3-pytest \
	python3-numpy

RUN apt update && apt install -y \
	  ros-humble-rclcpp \
	  ros-humble-moveit \
	  ros-humble-moveit-ros-control-interface

# Install additional ROS 2 packages
RUN apt-get install -y \
    ros-humble-teleop-twist-joy \
    ros-humble-teleop-twist-keyboard \
    ros-humble-navigation2 \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-eigen-stl-containers \
    ros-humble-random-numbers \
    ros-humble-moveit-common \
    ros-humble-nav2-bringup

RUN apt-get update && apt-get install -y ros-humble-ur-client-library \
                   ros-humble-moveit-servo \
                   ros-humble-warehouse-ros-sqlite \
                   ros-humble-controller-manager \
                   ros-humble-hardware-interface \
                   ros-humble-ur-msgs \
                   ros-humble-force-torque-sensor-broadcaster \
                   ros-humble-joint-state-broadcaster \
                   ros-humble-joint-state-publisher \
                   ros-humble-joint-trajectory-controller \
                   ros-humble-pose-broadcaster \
                   ros-humble-position-controllers \
                   ros-humble-ros2-controllers-test-nodes \
                   socat \
                   ros-humble-velocity-controllers \
                   ros-humble-controller-interface \
                   ros-humble-realtime-tools \
                   ros-humble-hardware-interface-testing \
                   ros-humble-ros2-control-test-assets \
                   liburdfdom-tools \
                   ros-humble-joint-state-publisher-gui \
                   ros-humble-gazebo-ros2-control \
                   ros-humble-ament-clang-format \
                   ros-humble-slam-toolbox \
                   ros-humble-turtlebot3 \
                   ros-humble-turtlebot3-simulations \
                   ros-humble-ros2-control \
                   ros-humble-ros2-controllers \
                   ros-humble-gripper-controllers \
                   ros-humble-xacro \
                   ros-humble-ament-clang-tidy \
                   ros-humble-apriltag \
                   ros-humble-apriltag-ros
    
# Initialize rosdep
RUN rosdep init && rosdep update

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc 
RUN echo 'export ROS_DOMAIN_ID=30 #TURTLEBOT3' >> ~/.bashrc
RUN echo 'source /usr/share/gazebo/setup.sh' >> ~/.bashrc
RUN echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
RUN echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc

#COPY play_with_scan.ipynb /ws_slam
#RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /ws_slam

# Entry point: Open a bash shell with sourced ROS environment
#ENTRYPOINT ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && source ~/ws_moveit/install/setup.bash && exec bash"]
