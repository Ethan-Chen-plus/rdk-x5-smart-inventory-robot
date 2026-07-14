#!/usr/bin/env python3
"""Publish microphone RMS level from the Magic Box ALSA capture device."""

import audioop
import subprocess
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class AudioActivity(Node):
    def __init__(self) -> None:
        super().__init__("audio_activity")
        self.publisher = self.create_publisher(Float32, "/audio/activity", 10)
        self.process = subprocess.Popen(
            [
                "arecord",
                "-q",
                "-D",
                "hw:0,0",
                "-f",
                "S32_LE",
                "-r",
                "16000",
                "-c",
                "2",
                "-t",
                "raw",
            ],
            stdout=subprocess.PIPE,
        )
        self.thread = threading.Thread(target=self.read_audio, daemon=True)
        self.thread.start()
        self.get_logger().info("publishing microphone RMS on /audio/activity")

    def read_audio(self) -> None:
        while rclpy.ok() and self.process.stdout:
            chunk = self.process.stdout.read(12800)
            if not chunk:
                break
            normalized_rms = audioop.rms(chunk, 4) / 2147483648.0
            self.publisher.publish(Float32(data=float(normalized_rms)))

    def close(self) -> None:
        self.process.terminate()
        self.process.wait(timeout=2)


def main() -> None:
    rclpy.init()
    node = AudioActivity()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
