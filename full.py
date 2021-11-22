"""A single entry command used by PyEmpaq to run the whole process. As you can see, there are some harcoded things. TODO: Implement better"""

import sys
import subprocess
from pathlib import Path

if len(sys.argv) != 4:
    print("Usar: fotos2imagen.pyz <dir_con_fotos> <foto_a_emular.jpg> <foto_salida.jpg>")
    exit()

source_dir = sys.argv[1]
source_image = sys.argv[2]
output_file = sys.argv[3]

preprocess_dir = source_dir + "--preprocessed"
Path(preprocess_dir).mkdir(exist_ok=True)


subprocess.run([
    "python",
    "preprocess.py",
    source_dir,
    preprocess_dir,
    "50",
    "200",
])

subprocess.run([
    "python",
    "fotos2imagen.py",
    source_image,
    output_file,
    "--force",
    "-w",
    "-c", "50",
    "-t", "200",
    "--images-root-dir", preprocess_dir,
])

