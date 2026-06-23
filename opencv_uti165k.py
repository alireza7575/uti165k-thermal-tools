import argparse
import struct
import sys
import time
from pathlib import Path


ROS_KINETIC_PATH = "/opt/ros/kinetic/lib/python2.7/dist-packages"
WINDOW_NAME = "Thermal Camera - Press Q to quit"
DEFAULT_WIDTH = 240
DEFAULT_HEIGHT = 321


def import_cv2_without_ros_python2_path():
    """Allow cv2 from Python 3 to import on older ROS Kinetic systems."""
    removed_ros_path = False
    if ROS_KINETIC_PATH in sys.path:
        sys.path.remove(ROS_KINETIC_PATH)
        removed_ros_path = True

    import cv2

    if removed_ros_path:
        sys.path.append(ROS_KINETIC_PATH)

    return cv2


cv2 = import_cv2_without_ros_python2_path()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Display a UTI165K thermal camera stream and read experimental temperature metadata."
    )
    parser.add_argument("--first-camera", type=int, default=0, help="First camera index to try.")
    parser.add_argument("--last-camera", type=int, default=5, help="Last camera index to try.")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="Requested camera width.")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="Requested camera height.")
    parser.add_argument(
        "--face-cascade",
        default="/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml",
        help="Path to OpenCV Haar cascade XML file. Leave missing to disable face detection.",
    )
    parser.add_argument("--temperature-threshold", type=float, default=40.0)
    return parser.parse_args()


def open_camera(first_camera, last_camera, width, height):
    for camera_num in range(first_camera, last_camera + 1):
        cam = cv2.VideoCapture(camera_num)
        if not cam.isOpened():
            print(f"Was not able to open camera {camera_num}")
            cam.release()
            continue

        if not cam.set(cv2.CAP_PROP_FRAME_WIDTH, width):
            print(f"Was not able to set camera {camera_num} width to {width} pixels")
            cam.release()
            continue

        if not cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height):
            print(f"Was not able to set camera {camera_num} height to {height} pixels")
            cam.release()
            continue

        actual_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if actual_width != width or actual_height != height:
            print(
                f"Camera {camera_num} opened at {actual_width} x {actual_height}, "
                f"expected {width} x {height}"
            )
            cam.release()
            continue

        return camera_num, cam

    raise RuntimeError(f"No camera opened from index {first_camera} to {last_camera}.")


def load_face_cascade(path):
    cascade_path = Path(path)
    if not cascade_path.exists():
        print(f"Face cascade not found: {cascade_path}. Face detection disabled.")
        return None

    cascade = cv2.CascadeClassifier(str(cascade_path))
    if cascade.empty():
        print(f"Could not load face cascade: {cascade_path}. Face detection disabled.")
        return None

    return cascade


def draw_faces(frame, cascade):
    if cascade is None:
        return

    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray_image, 1.1, 3, minSize=(80, 80))
    for x, y, w, h in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


def read_temperature(cam, height):
    cam.set(cv2.CAP_PROP_CONVERT_RGB, 0)
    try:
        ret, raw_frame = cam.read()
        if not ret:
            return None

        return struct.unpack("h", raw_frame[height - 1][0][0:2])[0] / 10
    finally:
        cam.set(cv2.CAP_PROP_CONVERT_RGB, 1)


def main():
    args = parse_args()
    camera_num, cam = open_camera(args.first_camera, args.last_camera, args.width, args.height)
    face_cascade = load_face_cascade(args.face_cascade)

    print(
        "Camera %d open at size: (%d x %d) %d FPS"
        % (
            camera_num,
            cam.get(cv2.CAP_PROP_FRAME_WIDTH),
            cam.get(cv2.CAP_PROP_FRAME_HEIGHT),
            cam.get(cv2.CAP_PROP_FPS),
        )
    )

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, args.width * 2, args.height * 2)

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                print("Failed to fetch frame")
                time.sleep(0.1)
                continue

            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            draw_faces(color_frame, face_cascade)
            cv2.imshow(WINDOW_NAME, color_frame)

            temperature = read_temperature(cam, args.height)
            if temperature is not None:
                print(f"Temp calculation (experimental): {temperature:.1f} C")
                if temperature > args.temperature_threshold:
                    print("High temperature detected")

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
