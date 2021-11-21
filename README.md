# fotos2imagen

The idea is to build an image composed by zillion small photos, aiming to play and learn.

## What you need to try this

- A zillion images that will be used as source

- The image you want to "reproduce" (we call it "original")


## Steps

- Create a virtualenv and install the dependencies

    ```bash
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

- Pre-process all source images so they are useful input for next setp

    ```bash
    mkdir -p downloads/processed
    python preprocess.py <source-dir> downloads/processed 50 200
    ```

  where source-dir is a directory with all your image sources; 50 and 200 are the sizes of the small squares to be replaced in the original image and the size of the replacing image in each small square.

- Run the find and replacement script

    ```bash
    python script.py <original-image> 50 200 output.jpeg
    ```