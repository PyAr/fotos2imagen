# fotos2imagen

The idea is to build an image composed by zillion small photos, aiming to play and learn.

## What you need to try this

- A zillion images that will be used as source

- The image you want to "reproduce" (we call it "original")


## Setup

Create a virtualenv and install the dependencies

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Preprocess

Pre-process all source images so they are useful input for next setp. This is necessary only once (or every time you want to update your images DB).

```bash
mkdir -p downloads/processed
python preprocess.py <source-dir> downloads/processed 50 200
```

where source-dir is a directory with all your image sources; 50 and 200 are the sizes of the small squares to be replaced in the original image and the size of the replacing image in each small square.

Only JPG images are supported.

## Create the mosaic

Run the mosaicking script

```bash
python fotos2imagen.py --help
python fotos2imagen.py imagenOriginal.jpg output.jpg \
  --chunk-size 50 \
  --tile-size 200 \
  --randomization 25 \
  --blend 0.15 \
  --images-root-dir downloads/processed \
  --show-progress-window
```

## Distribution

Using PyEmpaq >= 0.2.3 you can empaq this awsome lib and share to every OS ever known
```bash
pyempaq .
```

Until PyEmpaq allow it, make shure to remove every single file or directory that you want to omit. `venv`, `*.jpg`, `*.pkl`, and so on

