#!/usr/bin/env python3
import argparse
import enum
import hashlib
import logging
import os
import shutil
import subprocess
import sys
import threading
from collections import defaultdict
from datetime import datetime
from functools import partial
from multiprocessing.pool import ThreadPool as Pool
from pathlib import Path, PurePath

import exiftool
from dateutil.parser import parse as date_parse

from .base import EnumAction, ExtendedEnum

logger = logging.getLogger("dedupe_photos")

EXIF_DATE_TAGS = [
    "EXIF:DateTimeOriginal",
    "QuickTime:CreateDate",
    # "EXIF:ModifyDate",
]


class SupportedMedia(ExtendedEnum):
    IMAGE_HEIC = "image/heic"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_TIFF = "image/tiff"
    VIDEO_QUICKTIME = "video/quicktime"
    VIDEO_MSVIDEO = "video/x-msvideo"
    VIDEO_MP4 = "video/mp4"


def detect_file_mimetype(file_path):
    """
    Detects the MIME type for the given file path and returns it.
    Uses the `file` command, which makes it portable for any platform that it supports.
    """
    completed_process = subprocess.run(
        ["file", "--mime-type", file_path], capture_output=True
    )
    if completed_process.returncode > 0:
        logger.error("Unable to detect file mime type. Ensure that file is available.")
        sys.exit(10)
    return completed_process.stdout.decode().rsplit(":", 1)[-1].strip()


def parse_datetime(raw_datetime):
    # try multiple formats to parse
    try:
        converted = datetime.strptime(raw_datetime, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        converted = None
    return converted


def checksum(filename, blocksize=65536):
    hash = hashlib.blake2b()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()


def get_media_checksums(directory_path, supported_mime_types, checksums=None):
    if checksums is None:
        checksums = defaultdict(set)
    # traverse directory
    logger.info("Checksumming contents of %s", directory_path)
    for cur_path in directory_path.iterdir():
        if cur_path.is_file():
            # for each file detected as a photo
            file_type = detect_file_mimetype(cur_path)
            logger.debug(
                "Detected file type %s from path %s",
                file_type,
                cur_path,
            )
            if file_type in supported_mime_types:
                # store checksum with set of paths
                path_checksum = checksum(cur_path)
                checksums[path_checksum].add(cur_path)
        elif cur_path.is_dir():
            get_media_checksums(cur_path, supported_mime_types, checksums=checksums)
    return checksums


def organize_media(process_id, destination, checksums, helper):
    # run exiftool on cleaned paths
    for checksum, paths in checksums.items():
        logger.debug("Getting tags for paths %s", paths)
        metadata = helper.get_tags(paths, EXIF_DATE_TAGS)
        source_path = paths.pop()
        extension = source_path.suffix.lower()
        logger.info("Processing %s in %s", source_path, process_id)
        logger.debug("Metadata for %s:\n%s", source_path, metadata)
        # a number of possible metadata keys for change date
        raw_datetimes = [
            parse_datetime(found[key])
            for found in metadata
            for key in EXIF_DATE_TAGS
            if key in found
        ]
        logger.debug("Raw dates found for %s: %s", source_path, raw_datetimes)
        possible_datetimes = [
            raw_datetime for raw_datetime in raw_datetimes if raw_datetime is not None
        ]
        if not possible_datetimes:
            # TODO: do heuristic on path if exiftool fails
            pass
        if possible_datetimes:
            logger.debug(
                "Date times matched for %s: %s", source_path, possible_datetimes
            )
            confirmed_datetime = possible_datetimes[0]
            # build file name from datetime
            file_directory = Path(
                destination,
                f"{confirmed_datetime.year}",
                f"{confirmed_datetime.month}".zfill(2),
            )
            file_name = (
                f"{confirmed_datetime.year:04}"
                f"{confirmed_datetime.month:02}"
                f"{confirmed_datetime.day:02}-"
                f"{confirmed_datetime.hour:02}"
                f"{confirmed_datetime.minute:02}"
                f"{confirmed_datetime.second:02}-"
                f"{process_id}"
                f"{extension}"
            )
        else:
            logger.info("%s unsorted", source_path)
            file_directory = Path(destination, "Unsorted")
            file_name = source_path.name
        # copy path to organised destination
        if not file_directory.exists():
            file_directory.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, Path(file_directory, file_name))
        # TODO: update with exiftool to match calculated date


def organize_media_chunk(destination, checksums):
    with exiftool.ExifToolHelper() as helper:
        # TODO: maybe make this unique across script invocations?
        process_id = threading.get_ident()
        logger.info("Processing chunk with process %s", process_id)
        organize_media(process_id, destination, checksums, helper)


def main():
    parser = argparse.ArgumentParser(description="Manipulate a given media directory")
    parser.add_argument(
        "action", choices=["deduplicate"], help="action for media directory"
    )
    parser.add_argument("source", help="directory containing all files to traverse")
    parser.add_argument("destination", help="destination directory for cleaned media")
    parser.add_argument(
        "-m",
        "--media",
        type=SupportedMedia,
        nargs="*",
        action=EnumAction,
    )
    parser.add_argument(
        "-p",
        "--process-total",
        type=int,
        default=4,
        help="number of parallel processes to use",
    )
    parser.add_argument(
        "-l", "--log-level", default=logging.INFO, help="log level for the script"
    )

    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)

    supported_media = args.media or list(SupportedMedia)
    supported_mime_types = [media.value for media in supported_media]
    logger.debug("Checking for %s mime types", supported_mime_types)
    media_directory = Path(args.source)
    destination = Path(args.destination)
    if not media_directory.exists():
        logger.info("Directory %s does not exist", media_directory)
        sys.exit(1)
    if not destination.exists():
        destination.mkdir(parents=True)
    checksums = get_media_checksums(media_directory, supported_mime_types)
    logger.info("Found %s unique checksums", len(checksums))
    # TODO: dedupe paths by checking byte equality

    # break up checksums into chunks for parallel processing
    checksum_total = len(checksums)
    chunk_size = (checksum_total // args.process_total) + 1
    chunks = []
    current_chunk = {}
    for checksum, paths in checksums.items():
        current_chunk[checksum] = paths
        if len(current_chunk) >= chunk_size:
            chunks.append(current_chunk)
            current_chunk = {}
    if len(current_chunk) > 0:
        chunks.append(current_chunk)

    pool_fn = partial(organize_media_chunk, destination)
    with Pool(args.process_total) as pool:
        pool.map(pool_fn, chunks, 1)


if __name__ == "__main__":
    main()
