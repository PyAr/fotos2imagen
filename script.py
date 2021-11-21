import os
import sys
import random

import numpy as np

from PIL import Image

from pathlib import Path
from finder import ImageFinder



ROOT_DATA_DIR = "./downloads/processed/"


if __name__ == "__main__":
    source_image = Image.open(sys.argv[1])
    chunk_size = int(sys.argv[2])
    tile_size = int(sys.argv[3])
    out_fname = sys.argv[4]

    images_for_comparison = os.path.join(ROOT_DATA_DIR, f"{chunk_size}x{chunk_size}/")  # Se deriva de chunk_size
    target_images_directory = os.path.join(ROOT_DATA_DIR, f"{tile_size}x{tile_size}/")  # Se deriva de tile_size

    fisa = ImageFinder(
        images_path=Path(images_for_comparison), 
        window_height=chunk_size, 
        window_width=chunk_size,
    )
    # only once
    fisa.prepare()

    # Corto la imagen original para que entren chunks justos
    width, height = source_image.size
    width_in_chunks = width // chunk_size
    height_in_chunks = height // chunk_size
    n_chunks = width_in_chunks * height_in_chunks
    exceeding_cols = width % chunk_size
    exceeding_rows = height % chunk_size
    print(f"Entran {n_chunks} chunks")
    print(f"Entran {width_in_chunks} chunks a lo largo y sobran {str(exceeding_cols)} columnas")
    print(f"Entran {height_in_chunks} chunks a lo alto y sobran {str(exceeding_rows)} filas")

    box = (0, 0, width - exceeding_cols, height - exceeding_rows)
    useful_region = np.array(source_image.crop(box))
    # redefine
    width, height, _ = useful_region.shape

    
    mosaic_width = tile_size * width_in_chunks
    mosaic_height = tile_size * height_in_chunks
    mosaic = Image.new("RGB", (mosaic_width, mosaic_height), (255, 255, 255))

    for chunk_col in range(width_in_chunks):
        for chunk_row in range(height_in_chunks):
            # Chunk ini coords
            col_ini = chunk_col * chunk_size
            row_ini = chunk_row * chunk_size
            print(f"Chunk {chunk_col}, {chunk_row}: ({col_ini}, {row_ini})")

            chunk = useful_region[col_ini: col_ini + chunk_size, row_ini: row_ini + chunk_size]
            print(chunk.shape)
            filename = fisa.find_best_fit(chunk)  # Fisa's
            target_image_fname = os.path.join(target_images_directory, filename)
            target_image = Image.open(target_image_fname)
            
            start_x = chunk_col * tile_size
            start_y = chunk_row * tile_size
            mosaic.paste(target_image, (start_x, start_y))

    mosaic.save(out_fname)