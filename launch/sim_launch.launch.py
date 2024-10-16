import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription 
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import SetEnvironmentVariable
from launch_ros.substitutions import FindPackageShare
from launch.actions import (DeclareLaunchArgument, GroupAction,
                            IncludeLaunchDescription, TimerAction)


def generate_launch_description():
    pkg='my_robot'

    rsp= IncludeLaunchDescription(PythonLaunchDescriptionSource([os.path.join
                        (get_package_share_directory(pkg),'launch','rsp.launch.py')]),
                        launch_arguments={'use_sim_time':'true', 'use_ros2_control':'false'}.items())

    twist_param = os.path.join(get_package_share_directory(pkg),'config','twist_params.yaml')
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        parameters=[twist_param,{'use_sim_time':True}],
        remappings=[('/cmd_vel_out','/diff_cont/cmd_vel_unstamped')]
    )

    gazebo_params_file = os.path.join(get_package_share_directory(pkg),'config','gazebo_params.yaml')

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
                    launch_arguments={'extra_gazebo_args': '--ros-args --params-file ' + gazebo_params_file}.items()
             )


    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic','robot_description',
                                    '-entity','my_robot'],
                        output='screen')
    
    diff_drive_spawner = TimerAction(
            period=5.0,  # Delay to ensure controller_manager is up
            actions=[Node(
                package="controller_manager",
                executable="spawner",
                output="screen",
                arguments=["diff_cont"],
            )]
        )

    joint_broad_spawner = TimerAction(
            period=5.5,  # Slight delay after diff_drive_spawner
            actions=[Node(
                package="controller_manager",
                executable="spawner",
                output="screen",
                arguments=["joint_broad"],
            )]
    )

    return LaunchDescription([
        rsp,
        twist_mux,
        gazebo,
        spawn_entity,
        diff_drive_spawner,
        joint_broad_spawner,
    ])