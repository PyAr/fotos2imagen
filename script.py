import os
import sys
import pickle

import numpy as np

from PIL import Image
from tqdm import tqdm

from pathlib import Path
from finder import ImageFinder



ROOT_DATA_DIR = "./downloads/processed/"
DEFAULT_FISA_FNAME = "fisa.pkl"


def extract_chuk(chunk_col, chunk_row, chunk_size):
    # Chunk ini coords
    col_ini = chunk_col * chunk_size
    row_ini = chunk_row * chunk_size
    #print(f"Chunk {chunk_col}, {chunk_row}: ({col_ini}, {row_ini})"
    chunk = useful_region[col_ini: col_ini + chunk_size, row_ini: row_ini + chunk_size]
    return chunk

class Mosaiker:
    def __init__(self, source_image, chunk_size, tile_size, out_fname) -> None:

        self.images_for_comparison = os.path.join(ROOT_DATA_DIR, f"{chunk_size}x{chunk_size}/")  # Se deriva de chunk_size
        self.target_images_directory = os.path.join(ROOT_DATA_DIR, f"{tile_size}x{tile_size}/")  # Se deriva de tile_size

        self.fisa = self._load_a_fisa()

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

        self.useful_region = useful_region
        self.width = width
        self.height = height
        self.chunk_size = chunk_size
        self.width_in_chunks = width_in_chunks
        self.height_in_chunks = height_in_chunks
        self.n_chunks = n_chunks
        
        mosaic_width = tile_size * width_in_chunks
        mosaic_height = tile_size * height_in_chunks
        self._mosaic = Image.new("RGB", (mosaic_width, mosaic_height), (255, 255, 255))

    def _load_a_fisa(self):
        # if os.path.exists(DEFAULT_FISA_FNAME):
        #     print("Found a Fisa! Let's use it...")
        #     f = open(DEFAULT_FISA_FNAME, "rb").read()
        #     return pickle.load(f)

        fisa = ImageFinder(
            images_path=Path(self.images_for_comparison), 
            window_height=chunk_size, 
            window_width=chunk_size,
        )
        # only once
        fisa.prepare()
        pickle.dump(fisa, open(DEFAULT_FISA_FNAME, "wb"))
        return fisa

    def do_it(self):
        """just do it"""

        self.tiles = []
        for chunk_col in tqdm(range(self.width_in_chunks)):
            for chunk_row in range(self.height_in_chunks):
                chunk = self._extract_chunk(chunk_col, chunk_row)
                filename = self.fisa.find_best_fit(chunk)  # Fisa's
                self.tiles.append((chunk_col, chunk_row, filename))

        self._put_tiles()
        
    def _extract_chunk(self, chunk_col, chunk_row):
        """Extract a chunk from the original image."""

        col_ini = chunk_col * self.chunk_size
        row_ini = chunk_row * self.chunk_size
        #print(f"Chunk {chunk_col}, {chunk_row}: ({col_ini}, {row_ini})")
        chunk = self.useful_region[col_ini: col_ini + self.chunk_size, row_ini: row_ini + self.chunk_size]
        return chunk
    
    def _put_tiles(self):
        """Put a single tile in the output mosaic."""
        for chunk_col, chunk_row, filename in self.tiles:
            target_image_fname = os.path.join(self.target_images_directory, filename)
            target_image = Image.open(target_image_fname)
            start_x = chunk_col * tile_size
            start_y = chunk_row * tile_size
            self._mosaic.paste(target_image, (start_y, start_x))
            
        self._mosaic.save(out_fname)


if __name__ == "__main__":
    source_image = Image.open(sys.argv[1])
    chunk_size = int(sys.argv[2])
    tile_size = int(sys.argv[3])
    out_fname = sys.argv[4]

    mosaiker = Mosaiker(source_image, chunk_size, tile_size, out_fname)
    mosaiker.do_it()
