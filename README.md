# urc_machiato_arm

## Running Instructions
1. Download ROS2 Humble onto your machine (or Ubuntu or some other VM)
2. start the camera (dependent on camera)
```
source install/setup.bash # optionally: source /opt/ros/humble/setup.bash
ros2 launch depthai_ros_driver camera.launch.py
```
3. to see this on rviz2:
```
source install/setup.bash # optionally: source /opt/ros/humble/setup.bash
ros2 topic list | grep oak #optional
rviz2
```
4. use these commands to run the ros2 package
```
colcon build
source install/setup.bash # optionally: source /opt/ros/humble/setup.bash
ros2 run keyboard_typing autonomous_typing
```
