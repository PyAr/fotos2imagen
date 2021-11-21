import click

from mosaic import Mosaiker

ROOT_DATA_DIR = "./downloads/processed/"
DEFAULT_FISA_TEMPLATE = "fisa-{chunk_size}.pkl"


@click.command(name="mosaic")
@click.argument("source-image")
@click.argument("output-fname")
@click.option(
    "-c", 
    "--chunk-size", 
    default=50, 
    help="Edge size (in pixels) of the squares to process. The smaller the number then the higher "
         "the resolution of the output but slower to process. Images preprocessed with this chunk "
         "size must exist (or else a trained model). Default: 50."
)
@click.option(
    "-t",
    "--tile-size", 
    default=200,
    help="Tile size (in pixels) for the resulting mosaic. The higher the number then the bigger "
         "(heavier) will be the resulting mosaic. Default: 200."
)
@click.option(
    "-r",
    "--randomization", 
    default=25,
    help="When searching for tiles, take into account several options to reduce the reutilization of target images."
)
@click.option(
    "-b",
    "--blend", 
    default=0.1,
    help="Tiles post-processing factor. 0 does nothing, 0.99 results in the original image."
)
@click.option(
    "--images-root-dir", 
    default=ROOT_DATA_DIR,
    help="Directory with the preprocessed data."
)

@click.option(
    "--model-file", 
    default=None,
    help="Path to a pickled model file."
)
def main(source_image, output_fname, chunk_size, tile_size, randomization, blend, images_root_dir, model_file):
    """Recreate the given source image with a mosaic of other images."""

    mosaiker = Mosaiker(source_image, chunk_size, tile_size, output_fname, images_root_dir, model_file)
    mosaiker.do_it(randomization_factor=randomization, blend_factor=blend)


if __name__ == "__main__":
    main()

