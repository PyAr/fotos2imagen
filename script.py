import os
import logging
import sys
import pickle

import numpy as np

from PIL import Image
from tqdm import tqdm

from pathlib import Path
from finder import ImageFinder


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



ROOT_DATA_DIR = "./downloads/processed/"
DEFAULT_FISA_TEMPLATE = "fisa-{chunk_size}.pkl"


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
        useful_region = source_image.crop(box)
        # redefine
        width, height = useful_region.size

        self.useful_region = useful_region
        self.width = width
        self.height = height
        self.chunk_size = chunk_size
        self.width_in_chunks = width_in_chunks
        self.height_in_chunks = height_in_chunks
        self.n_chunks = n_chunks
        self.tile_size = tile_size
        
        self.fisa = self._load_a_fisa()

        mosaic_width = tile_size * width_in_chunks
        mosaic_height = tile_size * height_in_chunks
        self._mosaic = Image.new("RGB", (mosaic_width, mosaic_height), (255, 255, 255))

    def _load_a_fisa(self):
        target_fisa = DEFAULT_FISA_TEMPLATE.format(chunk_size=self.chunk_size)
        if os.path.exists(target_fisa):
            print(f"Found a Fisa for chunks size {self.chunk_size}! Let's use it...")
            with open(target_fisa, "rb") as f:
                return pickle.load(f)

        fisa = ImageFinder(
            images_path=Path(self.images_for_comparison), 
            window_height=self.chunk_size, 
            window_width=self.chunk_size,
        )
        # only once
        fisa.prepare()
        with open(target_fisa, "wb") as f:
            pickle.dump(fisa, f)
        return fisa

    def do_it(self):
        """just do it"""

        #import ipdb; ipdb.set_trace()
        try:
            for chunk_row in tqdm(list(range(self.height_in_chunks))):
                #print(f"Chunk Fila {chunk_row}")
                for chunk_col in range(self.width_in_chunks):
                    #print(f"Chunk Columna {chunk_col}")
                    chunk = self._extract_chunk(chunk_col, chunk_row)
                    filename = self.fisa.find_best_fit(chunk)  # Fisa's
                    self._put_single_tile_in_mosaic(chunk_col, chunk_row, filename)
        except ValueError as e:
            logger.exception(e)
            print("Falló. A llorar al campito 😭")
        
        
    def _extract_chunk(self, chunk_col, chunk_row):
        """Extract a chunk from the original image."""

        col_ini = chunk_col * self.chunk_size
        row_ini = chunk_row * self.chunk_size
        # En numpy las coords son (y, x) o sea (row, col)
        box = (col_ini, row_ini, col_ini + self.chunk_size, row_ini + self.chunk_size)
        #print("Chunk box: " + str(box))
        chunk = self.useful_region.crop(box)
        return np.array(chunk)

    def _put_single_tile_in_mosaic(self, chunk_col, chunk_row, filename):
        target_image_fname = os.path.join(self.target_images_directory, filename)
        target_image = Image.open(target_image_fname)
        start_col = chunk_col * self.tile_size
        start_row = chunk_row * self.tile_size
        tile_upper_left_coords = (start_col, start_row)
        #print("Tile box: " + str(tile_upper_left_coords))
        self._mosaic.paste(target_image, tile_upper_left_coords)
        self._mosaic.save(out_fname)


if __name__ == "__main__":
    source_image = Image.open(sys.argv[1])
    chunk_size_arg = int(sys.argv[2])
    tile_size_arg = int(sys.argv[3])
    out_fname = sys.argv[4]

    mosaiker = Mosaiker(source_image, chunk_size_arg, tile_size_arg, out_fname)
    mosaiker.do_it()
