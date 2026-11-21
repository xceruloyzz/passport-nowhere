"""Write the Valtoria passport spread to the grading output folder.

The spread is drawn procedurally by tools/generate_passport.py
(Pillow, fixed data, no network, no clock, no randomness beyond a
fixed seed), so every run produces the same image. If Pillow is
unavailable in the sandbox, the program falls back to the identical
image committed in this repository as entry.png.

The output folder is picked in this order:
1. the directory named by MAKEFUN_OUTPUT_DIR, when that variable is set;
2. /output, when that directory already exists;
3. ./out, as a local fallback.
"""

import os
import shutil
import sys
from pathlib import Path


def choose_destination() -> Path:
    """Pick the output folder using the priority listed above."""
    wanted = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if wanted:
        return Path(wanted)
    if Path("/output").is_dir():
        return Path("/output")
    return Path("out")


def render(here: Path):
    """Draw the spread with Pillow; return the image or None."""
    try:
        sys.path.insert(0, str(here / "tools"))
        from generate_passport import draw_spread

        return draw_spread()
    except Exception as exc:  # noqa: BLE001 - any failure falls back
        print(f"procedural render failed ({exc}); using entry.png",
              file=sys.stderr)
        return None


def main() -> int:
    here = Path(__file__).resolve().parent
    destination_dir = choose_destination()
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "entry.png"

    image = render(here)
    if image is not None:
        image.save(destination, format="PNG", optimize=True)
        print(f"rendered entry.png to {destination}")
        return 0

    source = here / "entry.png"
    if not source.is_file():
        print("entry.png is missing from the repository root",
              file=sys.stderr)
        return 1
    shutil.copyfile(source, destination)
    print(f"copied entry.png to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
