# Stage 2 Submission Package

Version: 0.1  
Updated: 2026-06-05

## Participant

- Name: Kewei Chen
- Project: TuntunClaw RDK X5
- Track: Smart Life Robotics
- Repository: https://github.com/Suibian-YY-pro/rdk-x5-smart-inventory-robot
- Discord thread: https://discord.com/channels/1300358874280230994/1503706103752429618/threads/1506248828523905105
- Official showcase PR: https://github.com/D-Robotics/Robotics-Dream-Keeper-Challenge/pull/1

## Stage 2 Goal

Stage 2 turns the Stage 1 RDK X5 bring-up into a full robot design. The planned system uses RDK X5 BPU inference, a camera, inventory state management, optional Feishu Bitable synchronization, and a real robotic arm to demonstrate a smart household inventory assistant.

This design is the physical-edge version of the completed TuntunClaw MuJoCo
prototype. The simulation already supports OpenClaw orchestration, VLM + SAM
segmentation, GraspNet grasp inference, continuous manipulation tasks,
persistent scene state, and inventory/location memory. Stage 3 focuses on
connecting the verified RDK X5 perception and Magic Box interaction path to the
real-arm control layer.

## Deliverable Checklist

| Official Requirement | Status | Repository Evidence |
|---|---|---|
| GitHub project or equivalent roadmap | Ready | `docs/ROADMAP.md` |
| Markdown proposal | Ready | `docs/PROPOSAL.md` |
| Architecture diagrams | Ready | `docs/ARCHITECTURE.md` |
| ROS 2 node graph | Ready | `docs/ARCHITECTURE.md` |
| Compute allocation | Ready | `docs/ARCHITECTURE.md` |
| BOM | Ready | `hardware/BOM.md` |
| Risk analysis | Ready | `docs/RISK_ANALYSIS.md` |
| Community share | Draft ready | See Discord post draft below |

## Concept and Application Design

### Scenario

The robot operates in an indoor shelf, desk, or storage-box scene. It observes household supply items with an RDK X5-connected camera, updates inventory state, and generates low-stock or location reminders. The final demo will use a controlled set of household objects so the perception and arm interaction can be repeatable.

### User

The target user is a home user, maker, or robotics learner who wants a practical smart home robot prototype rather than a stock AI demo. The primary interaction mode is visual inventory checking, structured status output, and optionally a voice or manual trigger for robotic arm actions.

### Core AI Capabilities

- Detect or classify household supply items on RDK X5.
- Stabilize observations across frames.
- Convert visual observations into inventory records.
- Detect low-stock, missing, or selected-item events.
- Trigger safe robotic arm actions such as pointing, moving, or sorting demo objects.

### Innovation and Differentiation

The project connects edge AI perception with a real household workflow and a physical robotic arm. The non-trivial part is not just running YOLO, but building a complete RDK X5-centered loop:

```text
camera -> BPU inference -> inventory state -> task planner -> safety gate -> robotic arm action
```

Target measurable goals:

- 10+ FPS detection pipeline for the demo scene.
- Below 2 seconds from item observation to inventory state update.
- At least one repeatable real-arm action linked to the detected or selected item.
- Public documentation with setup steps, evidence, and benchmark logs.

## Architecture Summary

See `docs/ARCHITECTURE.md` for the full system design. The high-level modules are:

- Camera capture and preprocessing.
- RDK X5 BPU object detection.
- Perception fusion and inventory state management.
- Feishu Bitable synchronization as optional external record keeping.
- Task planner, safety gate, and robotic arm control.

## Engineering Plan

### Stage 1 Foundation

Completed evidence includes:

- RDK X5 / Magic Box system access through SSH.
- XFCE desktop screenshot.
- Wi-Fi and network connectivity logs.
- MIPI camera live YOLO pipeline evidence.
- BPU static YOLO evidence.
- Microphone recording evidence.

See `docs/STAGE1_SUBMISSION.md`.

### Stage 2 Work

- Freeze the system architecture and ROS 2 node graph.
- Define inventory record schema and Feishu sync behavior.
- Choose the first robotic arm action: pointing before grasping.
- Prepare benchmark plan for BPU inference and end-to-end latency.
- Publish the Stage 2 summary in the Discord thread.

### Stage 3 Work

- Implement a minimal end-to-end pipeline.
- Record BPU and live perception benchmarks.
- Add real robotic arm action.
- Produce a 3-7 minute demo video.
- Update the official showcase PR with final links.

## Community Post Draft

```text
Stage 2 Preview - 2026-06-05

I have completed the initial RDK X5 setup and Stage 1 evidence collection. The project is moving toward a smart household inventory assistant powered by RDK X5 and a real robotic arm.

Current focus:
- On-device perception with RDK X5 BPU
- Household item detection and inventory tracking
- Robotic arm interaction for simple item handling or demonstration
- ROS 2-based system architecture
- Reproducible documentation and demo pipeline

Project repository:
https://github.com/Suibian-YY-pro/rdk-x5-smart-inventory-robot

Stage 1 package:
https://github.com/Suibian-YY-pro/rdk-x5-smart-inventory-robot/blob/master/docs/STAGE1_SUBMISSION.md

Stage 2 design draft:
https://github.com/Suibian-YY-pro/rdk-x5-smart-inventory-robot/blob/master/docs/STAGE2_SUBMISSION.md

Official showcase PR:
https://github.com/D-Robotics/Robotics-Dream-Keeper-Challenge/pull/1

Next:
I will refine the prototype pipeline, benchmark plan, and robotic arm demonstration for Stage 3.

#RoboticsDreamKeeper #RDKX5
```
