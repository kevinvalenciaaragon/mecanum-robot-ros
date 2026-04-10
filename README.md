# Mecanum Mobile Robot with ROS

ROS-based control, obstacle avoidance and 2D mapping stack for a mecanum-wheel mobile robot platform.

## Overview
This repository showcases a robotics project focused on the development of a mecanum mobile robot using ROS. The system integrates:

- **Holonomic motion control** for a 4-wheel mecanum platform
- **Keyboard teleoperation** for real-time manual driving
- **LIDAR-based obstacle avoidance** as a safety layer
- **Odometry estimation** from encoder feedback
- **2D mapping workflow** using **RPLidar** and **Hector SLAM**

The project was developed as part of an academic robotics workstream and is presented here as a technical portfolio repository.

## Key Capabilities
- Real-time robot motion control using mecanum kinematics
- Teleoperation with linear and angular velocity commands
- Safe command arbitration using LIDAR scan data
- Odometry publishing through ROS topics
- Remote ROS operation between robot hardware and control station
- Map generation and saving workflow for indoor environments

## System Architecture
The core ROS application is organized around custom nodes:

- **`mecanum_controller.py`**  
  Receives velocity commands, applies mecanum-drive kinematics, reads encoder data, and publishes odometry.

- **`realtime_teleop_v2.py`**  
  Publishes teleoperation commands from keyboard input.

- **`obstacle_avoider.py`**  
  Acts as a safety layer between teleop and low-level control by evaluating LIDAR data and deciding whether to keep or modify the requested motion command.

In the original project documentation, the robot bring-up launches the control stack and the LIDAR node, while the mapping workflow uses RPLidar data together with Hector SLAM and `map_server` for map generation and saving.



## Hardware Stack
- Raspberry Pi 4b as onboard computer
- RPLidar sensor
- Roboclaw-based motor driver interface
- 4-wheel mecanum base
- Wheel encoders

## Software Stack
- ROS (Kinetic/Noetic depending on machine role)
- Python ROS nodes
- `rplidar_ros`
- `hector_slam`
- `map_server`
- Standard ROS packages for `tf`, `nav_msgs`, `geometry_msgs`, and `sensor_msgs`

## Installation
Create a Catkin workspace and clone this repository inside `src/`:

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
git clone https://github.com/kevinvalenciaaragon/mecanum-robot-ros.git
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

Install the required ROS dependencies.

Example packages used by the project:

```bash
sudo apt-get install ros-noetic-hector-slam
sudo apt-get install ros-noetic-map-server
```

If your setup requires additional third-party packages such as `rplidar_ros`, install them separately and document their source clearly.

## Running the Robot
### 1. Build and source the workspace
```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### 2. Start the robot control stack
```bash
roslaunch mecanum_robot robot.launch
```

### 3. Start mapping workflow
Bring up the LIDAR node and run the SLAM launch file:

```bash
roslaunch rplidar_ros rplidar.launch
roslaunch hector_slam_launch tutorial.launch
```

### 4. Save a generated map
```bash
mkdir -p ~/catkin_ws/maps
cd ~/catkin_ws/maps
rosrun map_server map_saver -f my_map
```

## ROS Interfaces
### Main topics
- `/cmd_vel` — safe motion command consumed by the controller
- `/cmd_vel_teleop` — teleoperation command
- `/scan` — LIDAR scan data
- `/odom` — odometry output

## Engineering Notes
- The obstacle avoidance node is designed as an intermediate decision layer rather than a separate planner.
- The project supports a distributed ROS configuration where the robot hardware and the operator station run on different machines.
- For a public repository, all IP addresses, usernames, passwords, and local network settings must be replaced with placeholders.

## Results and Demonstration
Recommended media to add in `docs/media/`:
- Photo of the robot platform
- Screenshot of the ROS graph
- RViz screenshot during mapping
- Short GIF or video of teleoperation and obstacle avoidance
- Example generated map

## Future Improvements
- Refactor parameters into YAML configuration files
- Replace hardcoded setup steps with reproducible launch/config files
- Add simulation support in Gazebo
- Add autonomous waypoint navigation
- Add CI checks for Python formatting and linting
- Add a URDF model and TF tree diagram

## Why this repository matters
This project demonstrates practical skills in:
- Mobile robotics
- ROS node development
- Sensor integration
- Motion control
- Safety-layer design
- System bring-up and field testing

## Author
**Kevin Valencia-Aragón**  
Robotics / Control / Automation Engineer  
LinkedIn: `https://www.linkedin.com/in/kevin-gabriel-valencia-arag%C3%B3n-1a2782127/`  


---

> Note: this repository is intentionally organized as a clean portfolio version of the project, not as a raw backup of the original workspace.
