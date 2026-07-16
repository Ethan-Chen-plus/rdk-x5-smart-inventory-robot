# Reference Repositories

Updated: 2026-05-19

## RDK X5 / D-Robotics References

| Repository | Why It Matters |
|---|---|
| https://github.com/D-Robotics/rdk_model_zoo | Primary model deployment reference for RDK boards. Use this first for Stage 1 AI demo evidence. |
| https://github.com/D-Robotics/hobot_dnn | D-Robotics DNN runtime reference for BPU-oriented deployment. |
| https://github.com/D-Robotics/hobot_mipi_cam | Camera bring-up reference for MIPI camera paths. |
| https://github.com/D-Robotics/hobot_stereonet | Stereo depth example for RDK X5 with ROS 2 and camera input. Useful if depth perception becomes necessary. |
| https://github.com/D-Robotics/body_tracking | Visual tracking and robot-control style reference for ROS 2 integration patterns. |
| https://github.com/D-Robotics/xiaozhi-in-rdk | Audio and interaction reference on RDK X5. |

## Community RDK X5 Examples

| Repository | Why It Matters |
|---|---|
| https://github.com/WSJ261126/RDK-X5-YOLOv5-Deploy | Practical YOLOv5 training, quantization, and deployment guide for RDK X5 BPU. |
| https://github.com/WSJ261126/RDK-X5-YOLO-Robot | RDK X5 + ROS 2 + BPU YOLO + robot car + arm manipulation example. Very close to the final integration style. |
| https://github.com/YahboomTechnology/RDK-X5-Robot-Car | RDK X5 robot car reference, useful for ROS 2 hardware integration patterns. |
| https://github.com/YahboomTechnology/ROSMASTER-M1 | ROS 2 robot platform that lists RDK X5 support. Useful for system architecture comparison. |

## Robotics / Manipulation References

| Repository | Why It Matters |
|---|---|
| https://github.com/elephantrobotics/mycobot_ros | ROS package for myCobot robots. Useful as a reference if the real arm is myCobot-like. |
| https://github.com/ros-planning/moveit2 | Standard ROS 2 manipulation framework. Useful for Stage 2 architecture, even if Stage 3 uses a simpler control path. |
| https://github.com/ros2/ros2 | Core ROS 2 ecosystem reference. |
| https://github.com/huggingface/lerobot | LeRobot 0.6.0 and SmolVLA training/deployment reference used by the final physical system. |

## Inventory / App References

| Repository | Why It Matters |
|---|---|
| https://github.com/COS301-SE-2024/Smart-Inventory | Smart inventory system reference for inventory state, roles, and workflows. Not robotics-specific, but useful for data model ideas. |

## Suggested Starting Point

For Stage 1, start from:

1. `D-Robotics/rdk_model_zoo`
2. `WSJ261126/RDK-X5-YOLOv5-Deploy`
3. `D-Robotics/hobot_mipi_cam` or a USB camera path depending on the camera hardware

For the delivered Stage 2-3 system, the main references are:

1. `WSJ261126/RDK-X5-YOLO-Robot` for an RDK X5 + ROS 2 + manipulation reference.
2. `huggingface/lerobot` for SmolVLA fine-tuning and online policy inference.
3. ROKAE xCoreSDK 0.7.0 for the final ER3 Pro control interface. The vendor SDK itself is not redistributed.
