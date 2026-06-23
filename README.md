# UTI165 Thermal Imager

Python experiments for reading image and temperature data from a UTI165K thermal camera. The repository includes a live OpenCV viewer and an offline parser for captured frame data.

![UTI165 thermal camera output](https://user-images.githubusercontent.com/41507280/111019189-93d0e100-83f8-11eb-9022-e84d079466f9.png)

## Repository Contents

- `opencv_uti165k.py` - Opens the thermal camera with OpenCV, displays the video stream, detects faces, and reads an experimental temperature value from the raw frame data.
- `raw_thermal.py` - Parses captured frame data and exports thermal images as BMP files plus an animated `thermal.webp`.
- `uti165k capture.tdc` - Sample capture file kept for reference.

## Requirements

- Python 3
- OpenCV
- NumPy
- Pillow
- A UTI165K thermal camera connected as a video device

Install the Python packages:

```bash
pip install opencv-python numpy pillow
```

On Linux, make sure the current user has permission to access video devices such as `/dev/video0`.

## Live Camera Viewer

Run the OpenCV viewer:

```bash
python opencv_uti165k.py
```

The script tries camera indexes `0` through `5`, configures the camera at `240 x 321`, and opens a window named `Thermal Camera - Press Q to quit`.

Press `q` to close the viewer.

## Offline Frame Conversion

`raw_thermal.py` expects a CSV capture named `body_temp_cam.csv` in the working directory. It reads frame data from the CSV, converts the YUV frame bytes to RGB, and writes:

- `thermal001.bmp`, `thermal002.bmp`, etc.
- `thermal.webp`

Run it with:

```bash
python raw_thermal.py
```

## Notes

- Temperature calculation is experimental and depends on how the UTI165K encodes raw frame metadata.
- `opencv_uti165k.py` contains ROS Kinetic path handling for an older Linux/ROS environment. If you are not using ROS Kinetic, remove or adjust those `sys.path` lines.
- The face detection path points to the common Linux OpenCV Haar cascade location: `/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml`.

## Author

Alireza Ahmadi
