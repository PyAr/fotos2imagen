import os
import logging
import sys
import pickle

import numpy as np

from PIL import Image, ImageStat, ImageChops, ImageOps
from tqdm import tqdm

from pathlib import Path
from finder import ImageFinder
from image_progress import image_progress

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



DEFAULT_FISA_TEMPLATE = "fisa-{chunk_size}.pkl"
DEFAULT_RANDOMIZATION_FACTOR = 1


class Mosaiker:
    def __init__(self, source_image_path, chunk_size, tile_size, out_fname, images_root_dir, model_file=None) -> None:

        source_image = Image.open(source_image_path)

        self.images_for_comparison = os.path.join(images_root_dir, f"{chunk_size}x{chunk_size}/")  # Se deriva de chunk_size
        self.target_images_directory = os.path.join(images_root_dir, f"{tile_size}x{tile_size}/")  # Se deriva de tile_size

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
        self.out_fname = out_fname
        self.images_root_dir = images_root_dir
        
        self.fisa = self._load_a_fisa(model_file=model_file)

        mosaic_width = tile_size * width_in_chunks
        mosaic_height = tile_size * height_in_chunks
        self._mosaic = Image.new("RGB", (mosaic_width, mosaic_height), (255, 255, 255))

    def _load_a_fisa(self, model_file=None):
        """"""

        if model_file:
            # Use the provided file, blindly
            with open(model_file, "rb") as f:
                return pickle.load(f)
        
        target_fisa = DEFAULT_FISA_TEMPLATE.format(chunk_size=self.chunk_size)
        fisa_file_path = os.path.join(self.images_root_dir, target_fisa)
        if os.path.exists(fisa_file_path):
            # Look for an existing model in the default location
            print(f"Found a Fisa for chunks size {self.chunk_size}! Let's use it...")
            with open(fisa_file_path, "rb") as f:
                return pickle.load(f)

        # Let's just initialize a new Fisa and save it for reuse
        print(f"🔎  No Fisa in sight for chunks size {self.chunk_size}! Let's summon one...")
        fisa = ImageFinder(
            images_path=Path(self.images_for_comparison), 
            window_height=self.chunk_size, 
            window_width=self.chunk_size,
        )
        fisa.prepare()
        with open(fisa_file_path, "wb") as f:
            pickle.dump(fisa, f)
        return fisa

    def do_it(self, randomization_factor=DEFAULT_RANDOMIZATION_FACTOR, blend_factor=0, show_progress_window=False):
        """just do it"""

        #import ipdb; ipdb.set_trace()
        try:
            images = image_progress(
                base_image=self.out_fname,
                width=self.width,
                height=self.height,
                show_progress_window=show_progress_window,
                iterable=list(range(self.height_in_chunks))
            )
            for chunk_row in images:
                #print(f"Chunk Fila {chunk_row}")
                for chunk_col in range(self.width_in_chunks):
                    #print(f"Chunk Columna {chunk_col}")
                    chunk = self._extract_chunk(chunk_col, chunk_row)
                    filename = self.fisa.find(chunk, randomization_factor=randomization_factor)  # Fisa's
                    target_image_fname = os.path.join(self.target_images_directory, filename)
                    target_image = Image.open(target_image_fname)
                    tile = self._build_tile(chunk, target_image, blend_factor=blend_factor)
                    self._put_single_tile_in_mosaic(chunk_col, chunk_row, tile)
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

    def _put_single_tile_in_mosaic(self, chunk_col, chunk_row, target_image):
        start_col = chunk_col * self.tile_size
        start_row = chunk_row * self.tile_size
        tile_upper_left_coords = (start_col, start_row)
        self._mosaic.paste(target_image, tile_upper_left_coords)
        self._mosaic.save(self.out_fname)

    def _build_tile(self, chunk, target_image, blend_factor):
        # import ipdb; ipdb.set_trace()
        
        # chunk_per_channel_mean = np.mean(chunk, axis=tuple(range(chunk.ndim-1)))

        # tile_per_channel_mean = ImageStat.Stat(target_image).mean

        # per_channel_diff = chunk_per_channel_mean - tile_per_channel_mean

        # change_factor = per_channel_diff * 0.1
        fitted_chunk = ImageOps.fit(
            Image.fromarray(chunk),
            target_image.size
        )
        return ImageChops.blend(target_image, fitted_chunk, blend_factor)

