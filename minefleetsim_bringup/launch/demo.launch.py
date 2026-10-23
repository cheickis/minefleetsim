from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from pathlib import Path


def generate_launch_description():
    world = str(Path(get_package_share_directory('minefleetsim_description')) / 'worlds' / 'underground_demo.sdf')
    bridge = str(Path(get_package_share_directory('minefleetsim_bringup')) / 'config' / 'bridge.yaml')
    headless = LaunchConfiguration('headless')
    return LaunchDescription([
        DeclareLaunchArgument('headless', default_value='false', description='Gazebo server only'),
        ExecuteProcess(cmd=['gz', 'sim', '-r', world], output='screen', condition=UnlessCondition(headless)),
        ExecuteProcess(cmd=['gz', 'sim', '-s', '-r', world], output='screen', condition=IfCondition(headless)),
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='gz_bridge',
             parameters=[{'config_file': bridge}], output='screen'),
        Node(package='minefleetsim_fleet', executable='fleet_manager', output='screen'),
    ])
