# UTI165K Thermal Tools

Python tools for reading image and experimental temperature data from a UTI165K thermal camera. The repository includes a live OpenCV viewer and an offline converter for captured frame data.

![UTI165 thermal camera output](https://user-images.githubusercontent.com/41507280/111019189-93d0e100-83f8-11eb-9022-e84d079466f9.png)

## Repository Contents

- `opencv_uti165k.py` - Opens the thermal camera with OpenCV, displays the video stream, optionally detects faces, and reads an experimental temperature value from the raw frame data.
- `raw_thermal.py` - Parses CSV frame data and exports thermal images as BMP files plus an animated WebP.
- `uti165k capture.tdc` - Sample capture file kept for reference.
- `requirements.txt` - Python package dependencies.

## Requirements

- Python 3
- OpenCV
- NumPy
- Pillow
- A UTI165K thermal camera connected as a video device

Install the Python packages:

```bash
pip install -r requirements.txt
```

On Linux, make sure the current user has permission to access video devices such as `/dev/video0`.

## Live Camera Viewer

Run the OpenCV viewer:

```bash
python opencv_uti165k.py
```

The script tries camera indexes `0` through `5`, configures the camera at `240 x 321`, and opens a window named `Thermal Camera - Press Q to quit`.

Press `q` to close the viewer.

Useful options:

```bash
python opencv_uti165k.py --first-camera 0 --last-camera 5 --width 240 --height 321
python opencv_uti165k.py --face-cascade /path/to/haarcascade_frontalface_default.xml
```

## Offline Frame Conversion

`raw_thermal.py` expects a CSV capture with a `Data` column containing hex frame bytes. By default it looks for `body_temp_cam.csv` and writes output to `thermal_output/`.

- `thermal_output/thermal001.bmp`, `thermal_output/thermal002.bmp`, etc.
- `thermal_output/thermal.webp`

Run it with:

```bash
python raw_thermal.py
```

You can also choose the input file and output directory:

```bash
python raw_thermal.py capture.csv --output-dir output
```

## Notes

- Temperature calculation is experimental and depends on how the UTI165K encodes raw frame metadata.
- `opencv_uti165k.py` contains compatibility handling for older ROS Kinetic environments where Python 2 ROS paths can interfere with Python 3 OpenCV imports.
- The default face detection path points to the common Linux OpenCV Haar cascade location: `/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml`. If the file is missing, face detection is disabled and the thermal viewer still runs.

## Author

Alireza Ahmadi
