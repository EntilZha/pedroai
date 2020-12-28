import os
import subprocess
from typing import Dict, List, Union

import toml
from pydantic import BaseModel

from pedroai.log import get_logger

log = get_logger(__name__)

VERSION = "0.1.0"


class Options(BaseModel):
    create_dirs: bool
    directories: List[str]


class DownloadSpec(BaseModel):
    url: str
    checksum: str


class Job(BaseModel):
    name: str
    command: str
    check: str


class Config(BaseModel):
    version: str
    options: Options
    downloads: Dict[str, Union[str, DownloadSpec]]
    jobs: Dict[str, Job]


def _download_file(remote_file: str, local_file: str, dry_run: bool = False):
    if not dry_run:
        subprocess.run(
            f"curl -f --create-dirs -o {local_file} {remote_file}",
            shell=True,
            check=True,
        )


def download_file(
    remote_file: str, local_file: str, overwrite=False, dry_run: bool = False
):
    if os.path.exists(local_file):
        if overwrite:
            log.info("Overwriting, Downloading %s to %s", remote_file, local_file)
            _download_file(remote_file, local_file, dry_run=dry_run)
        else:
            log.info("File exists, skipping download of: %s", local_file)
    else:
        log.info("Downloading %s to %s", remote_file, local_file)
        _download_file(remote_file, local_file, dry_run=dry_run)


def main(
    config_file: str = "files.toml",
    overwrite: bool = False,
    download: bool = True,
    dry_run: bool = False,
    enforce_version: bool = True,
):
    log.info("Configuration")
    log.info("config_file: %s", config_file)
    log.info("overwrite: %s", overwrite)
    log.info("download: %s", download)
    log.info("dry_run: %s", dry_run)
    log.info("enforce_version: %s", enforce_version)
    with open(config_file) as f:
        log.info("Validating: %s", config_file)
        config = Config(**toml.load(f))
        if config.version != VERSION:
            log.warning(
                "Mismatched configuration versions: %s (script) vs %s (config)",
                VERSION,
                config.version,
            )
            if enforce_version:
                raise ValueError("Configuration version mismatch not allowed")

    if config.options.create_dirs:
        log.info("Creating Directories")
        for directory in config.options.directories:
            log.info("Creating: %s", directory)
            if not dry_run:
                os.makedirs(directory, exist_ok=True)

    if download:
        for local_file, remote_file in config.downloads.items():
            if isinstance(remote_file, str):
                download_file(
                    remote_file, local_file, overwrite=overwrite, dry_run=dry_run
                )
            elif isinstance(remote_file, DownloadSpec):
                download_file(
                    remote_file.url, local_file, overwrite=overwrite, dry_run=dry_run
                )
            else:
                raise ValueError(f"Invalid type for remote_file: {type(remote_file)}")

    for job in config.jobs.values():
        log.info("Running: %s", job.command)
        if not dry_run:
            if os.path.exists(job.check):
                log.info("Check path exists, skipping: %s", job.check)
            else:
                subprocess.run(job.command, shell=True, check=True)
