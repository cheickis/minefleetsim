# MineFleetSim — independent underground fleet simulation

A standalone ROS 2 + Gazebo Sim prototype for coordinating **generic mining vehicles**. No WRAITH dependencies, model geometry, controls, or packages.

## Phase 1 demo
Two differential-drive prototype vehicles begin on opposite ends of a single-lane underground tunnel. A centralized ROS 2 fleet controller grants a **single exclusive tunnel lease**. One vehicle crosses; the other holds at its staging location until the first clears the tunnel. Both vehicles receive velocity commands, not teleports.

This first deliverable is a coordination proof-of-concept, **not** a validated mining vehicle dynamics or Nav2 autonomy solution. It uses odometry-based waypoint following rather than SLAM/Nav2 and perfect simulated communication.

## Requirements
- Ubuntu machine with ROS 2 installed, `rclpy`, `nav_msgs`, `geometry_msgs`, `launch`, `launch_ros`.
- Gazebo Sim (modern `gz sim`, tested compatibility target: Gazebo Harmonic / Sim 8).
- `ros_gz_bridge` from the matching ROS/Gazebo installation.

ROS 2 Humble + Gazebo Harmonic may require the appropriate ROS/Gazebo vendor or OSRF packages; ROS/Gazebo version compatibility should be checked on your system.

## Build and run
```bash
# Put this repository in a ROS workspace:
mkdir -p ~/minefleetsim_ws/src
cp -r MineFleetSim ~/minefleetsim_ws/src/  # if you're in the archive's parent folder
cd ~/minefleetsim_ws
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch minefleetsim_bringup demo.launch.py
```

`demo.launch.py` starts Gazebo, the parameter bridge, and the fleet manager. The controller waits for both vehicle odometry topics before starting. Terminal messages describe tunnel grants, release, and mission completion.

Optional headless run:
```bash
ros2 launch minefleetsim_bringup demo.launch.py headless:=true
```

## Observe
```bash
ros2 topic echo /minefleetsim/status
ros2 topic echo /robot_1/odom
ros2 topic echo /robot_2/cmd_vel
```

The status topic is `std_msgs/String`, intended for a simple first demo.

## Components
- `minefleetsim_description/worlds/underground_demo.sdf`: rock-themed ground, tunnel wall segments, two robot models.
- `minefleetsim_bringup/config/bridge.yaml`: Gazebo ↔ ROS 2 topic bridge.
- `minefleetsim_bringup/launch/demo.launch.py`: one-command demo launcher.
- `minefleetsim_fleet/minefleetsim_fleet/manager.py`: finite-state centralized traffic reservation and waypoint follower.
- `minefleetsim_fleet/test/test_logic.py`: deterministic reservation tests.

## Explicit assumptions and limitations
- The critical tunnel is defined by world **x ∈ [-3.0, 3.0]**, along y≈0. Staging points are at x=−5 and x=+5.
- Robots are generic skid/differential-drive test carts with simplified geometry and 2D controllers; vehicle mass, traction, clearance, grade, and braking distance are **not mine-calibrated**.
- One tunnel lease is granted at a time; the non-owner cannot advance from its staging position.
- Release uses an odometry crossing threshold plus a 0.5 m margin. For real systems, add vehicle footprint, stopping distance, uncertainty, and timeout/fault recovery before authorizing entry.
- E-stop, safety PLC, personnel detection, LOS/NLOS comms, and real mine maps are out of scope here.
- This prototype does **not** include Nav2 yet. Phase 2 will add a mine lane graph, task scheduler, fleet dashboard, localization and Nav2 adapters.

## Next milestones
1. Validate demo in your ROS/Gazebo installation and adjust any plugin/bridge discrepancies.
2. Replace geometry with a configurable tunnel network and intersections.
3. Introduce vehicle interfaces, lane segments, routes, task scheduling and reservations.
4. Add Nav2 per vehicle and monitoring of mission KPIs.
5. Add mine-specific payload cycles, charger/refuel stops, breakdowns and degraded comms.
