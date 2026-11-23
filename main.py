"""Copy the pre-rendered news image into the output directory.

The image (image.png) was drawn when this entry was built. This program
only copies it, so it runs on the standard library alone. The copy is
byte-identical on every run.
"""

import os
import shutil
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    source = here / "image.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)


if __name__ == "__main__":
    main()
