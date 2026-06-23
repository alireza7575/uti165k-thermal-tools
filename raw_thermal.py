import argparse
import csv
import struct
import sys
from pathlib import Path

from PIL import Image


FORMAT_DESCRIPTOR = bytes.fromhex(
    "1B 24 04 01 02 59 55 59 32 00 00 10 00 80 00 00 AA 00 38 9B 71 10 01 00 00 00 00"
)
FRAME_DESCRIPTOR = bytes.fromhex(
    "26 24 05 01 00 F0 00 41 01 00 40 19 01 00 C0 4B 03 00 08 07 00 2A 2C 0A 00 "
    "03 2A 2C 0A 00 40 42 0F 00 40 4B 4C 00 1E 24 05 02 00 00 05 D0 02 00 00 "
    "C2 01 00 00 C2 01 00 20 1C 00 40 4B 4C 00 01 40 4B 4C 00 0B 24 06 02 02 "
    "00 01 00 00 00 00 26 24 07 01 00 F0 00 41 01 00 40 19 01 00 C0 4B 03 00 "
    "08 07 00 2A 2C 0A 00 03 2A 2C 0A 00 40 42 0F 00 40"
)
EXPECTED_FRAME_BYTES = 154080
IMAGE_WIDTH = 240
IMAGE_HEIGHT = 321
VISIBLE_HEIGHT = 320


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert UTI165K CSV frame captures to BMP frames and an animated WebP."
    )
    parser.add_argument(
        "input_csv",
        nargs="?",
        default="body_temp_cam.csv",
        help="CSV capture file containing a Data column with hex frame bytes.",
    )
    parser.add_argument("--output-dir", default="thermal_output", help="Directory for generated images.")
    parser.add_argument("--webp-name", default="thermal.webp", help="Animated WebP output filename.")
    parser.add_argument("--duration-ms", type=int, default=40, help="Frame duration for animated WebP.")
    return parser.parse_args()


def yuv_to_rgb(y_value, u_value, v_value):
    red = (22987 * (v_value - 128)) >> 14
    green = (-5636 * (u_value - 128) - 11698 * (v_value - 128)) >> 14
    blue = (29049 * (u_value - 128)) >> 14
    return (
        min(255, max(0, y_value + red)),
        min(255, max(0, y_value + green)),
        min(255, max(0, y_value + blue)),
    )


def convert_frame(data):
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT))

    for offset in range(0, len(data), 4):
        y1 = data[offset]
        u_value = data[offset + 1]
        y2 = data[offset + 2]
        v_value = data[offset + 3]

        x = offset // 2 % IMAGE_WIDTH
        y = offset // 2 // IMAGE_WIDTH
        if y < VISIBLE_HEIGHT:
            image.putpixel((x, y), yuv_to_rgb(y1, u_value, v_value))
            image.putpixel((x + 1, y), yuv_to_rgb(y2, u_value, v_value))
        elif y == VISIBLE_HEIGHT:
            raw_temperature = struct.unpack("h", data[offset : offset + 2])[0]
            print(f"Frame metadata temperature value: {raw_temperature}")
            break

    return image


def iter_frame_data(csv_path):
    csv.field_size_limit(sys.maxsize)
    columns = {}

    with csv_path.open(newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row:
                continue

            if row[0].startswith("#"):
                if len(row) > 2:
                    row[0] = row[0][2:]
                    columns = {column_name: index for index, column_name in enumerate(row)}
                continue

            if "Data" not in columns:
                continue

            data = bytes.fromhex(row[columns["Data"]])
            if len(data) == EXPECTED_FRAME_BYTES:
                yield data


def main():
    args = parse_args()
    csv_path = Path(args.input_csv)
    output_dir = Path(args.output_dir)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV capture file not found: {csv_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    bpp = FORMAT_DESCRIPTOR[21]
    format_guid = FORMAT_DESCRIPTOR[5:21].hex()
    width, height = struct.unpack_from("<xxxxxHH", FRAME_DESCRIPTOR)
    print(f"Capture descriptor: {width} x {height}, {bpp} bpp, GUID {format_guid}")

    images = []
    for index, frame_data in enumerate(iter_frame_data(csv_path), start=1):
        image = convert_frame(frame_data)
        image.save(output_dir / f"thermal{index:03d}.bmp")
        images.append(image)

    if not images:
        raise RuntimeError(f"No {EXPECTED_FRAME_BYTES}-byte frames found in {csv_path}")

    images[0].save(
        output_dir / args.webp_name,
        save_all=True,
        lossless=True,
        append_images=images[1:],
        optimize=False,
        duration=args.duration_ms,
        loop=0,
    )
    print(f"Wrote {len(images)} frame(s) to {output_dir}")


if __name__ == "__main__":
    main()
