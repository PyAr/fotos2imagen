#!/usr/bin/fades

import argparse
import pathlib

from PIL import Image  # fades


def main(source_dir, sizes_dirs):
    """Main entry point."""
    for path in source_dir.iterdir():
        print("Processing", path)
        src_image = Image.open(path)
        print("    size:", src_image.size)

        print("    squaring")
        width, height = src_image.size
        square_images = []
        if width == height:
            # already square
            square_images.append((0, src_image))
        elif width > height:
            # landscape
            # 12 x 5
            #  -> 0 5
            #  -> 3 8
            #  -> 7 12
            top = 0
            bottom = height
            border = (width - height) // 2
            crops = [
                (0, height),
                (border, border + height),
                (width - height, width),
            ]
            for idx, (left, right) in enumerate(crops):
                new_image = src_image.crop((left, top, right, bottom))
                square_images.append((idx, new_image))
        else:
            # vertical
            left = 0
            right = width
            border = (height - width) // 2
            crops = [
                (0, width),
                (border, border + width),
                (height - width, height),
            ]
            for idx, (top, bottom) in enumerate(crops):
                new_image = src_image.crop((left, top, right, bottom))
                square_images.append((idx, new_image))

        for edge_size, dest_dir in sizes_dirs:
            print("    saving", edge_size)
            for idx, image in square_images:
                resized = image.resize((edge_size, edge_size), Image.LANCZOS)
                new_path = f"{path.stem}_{idx}{path.suffix}"
                resized.save(dest_dir / new_path, quality=95)


parser = argparse.ArgumentParser()
parser.add_argument("source_dir", type=pathlib.Path, help="The dir with source images.")
parser.add_argument(
    "parent_dest_dir", type=pathlib.Path,
    help="Where a new NxN dir will be created to leave processed images.")
parser.add_argument("edge_size", type=int, nargs="+", help="The size of the image edge.")
args = parser.parse_args()

if not args.source_dir.exists():
    print("Error: the source dir does not exist")
    exit()
if not args.parent_dest_dir.exists():
    print("Error: the parent dir does not exist")
    exit()

sizes_dirs = []
for size in args.edge_size:
    dest_dir = args.parent_dest_dir / f"{size}x{size}"
    if dest_dir.exists():
        print(f"Error: the real destination dir already exists! {dest_dir!r}")
        exit()
    dest_dir.mkdir()
    sizes_dirs.append((size, dest_dir))


main(args.source_dir, sizes_dirs)
