#!/usr/bin/env python3
import pyrealsense2 as rs
import numpy as np
import cv2
import time
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Record color video from an Intel RealSense camera."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="realsense_output.avi",
        help="Output video file (e.g. realsense_output.avi)",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=float,
        default=10.0,
        help="Recording duration in seconds (default: 10)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second for recording (default: 30)",
    )
    args = parser.parse_args()

    # Configure RealSense pipeline
    pipeline = rs.pipeline()
    config = rs.config()
    # Use first detected device, enable color stream at 640x480
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, args.fps)

    try:
        print("[INFO] Starting RealSense pipeline...")
        pipeline_profile = pipeline.start(config)

        # Get color stream intrinsics just to confirm resolution
        color_stream = pipeline_profile.get_stream(rs.stream.color)
        intr = color_stream.as_video_stream_profile().get_intrinsics()
        width, height = intr.width, intr.height
        print(f"[INFO] Color stream: {width}x{height} @ {args.fps} FPS")

        # OpenCV video writer
        fourcc = cv2.VideoWriter_fourcc(*"XVID")  # or "MJPG"
        out = cv2.VideoWriter(args.output, fourcc, args.fps, (width, height))

        if not out.isOpened():
            print("[ERROR] Could not open video writer.")
            pipeline.stop()
            sys.exit(1)

        print(f"[INFO] Recording to {args.output} for {args.duration} seconds...")
        print("[INFO] Press Ctrl+C to stop early.")

        start_time = time.time()

        while True:
            # Break on duration
            if time.time() - start_time > args.duration:
                print("[INFO] Finished recording duration.")
                break

            # Wait for a coherent color frame
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            # Convert to numpy array
            color_image = np.asanyarray(color_frame.get_data())

            # Write frame to video file
            out.write(color_image)

            # (Optional) Show preview window
            cv2.imshow("RealSense Color", color_image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[INFO] 'q' pressed. Stopping recording.")
                break

    except KeyboardInterrupt:
        print("\n[INFO] Keyboard interrupt received. Stopping recording.")
    finally:
        print("[INFO] Releasing resources...")
        try:
            pipeline.stop()
        except Exception:
            pass
        cv2.destroyAllWindows()
        if "out" in locals():
            out.release()

if __name__ == "__main__":
    main()
