import logging
from pathlib import Path
import typer
from rich.progress import track


app = typer.Typer()


@app.command()
def rmf(directory: Path, glob_pattern: str, dry_run: bool = False):
    files = list(directory.glob(glob_pattern))
    for f in track(files):
        if dry_run:
            logging.info("Dry run enabled, skipping delete: %s", f)
        else:
            if f.is_file():
                f.unlink()
