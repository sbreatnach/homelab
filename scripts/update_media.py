#!/usr/bin/env python3
import os
from pathlib import Path, PurePath
from collections import defaultdict
import argparse
import sys
import logging
import hashlib
import shutil
import threading
from multiprocessing.pool import ThreadPool as Pool
from datetime import datetime
from functools import partial

import magic
import exiftool
from dateutil.parser import parse as date_parse

logger = logging.getLogger('dedupe_photos')


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


def get_media_checksums(directory_path, checksums=None):
    if checksums is None:
        checksums = defaultdict(set)
    # traverse directory
    logger.info("Checksumming contents of %s", directory_path)
    for cur_path in directory_path.iterdir():
        if cur_path.is_file():
            # for each file detected as a photo
            file_type = magic.from_file(cur_path, mime=True)
            logger.debug(
                "Detected file type %s from path %s", file_type, cur_path,
            )
            if file_type in ['image/jpeg', 'video/quicktime', 'video/x-msvideo', 'video/mp4']:
                # store checksum with set of paths
                path_checksum = checksum(cur_path)
                checksums[path_checksum].add(cur_path)
        elif cur_path.is_dir():
            get_media_checksums(cur_path, checksums=checksums)
    return checksums


def organize_media(process_id, destination, checksums, helper):
    # run exiftool on cleaned paths
    for checksum, paths in checksums.items():
        metadata = helper.get_metadata(paths)
        source_path = paths.pop()
        extension = source_path.suffix.lower()
        logger.info("Processing %s", source_path)
        logger.debug("Metadata for %s:\n%s", source_path, metadata)
        # possible metadata keys for change date:
        # EXIF:DateTimeOriginal
        raw_datetimes = [
            parse_datetime(found[key])
            for found in metadata
            for key in [
                "EXIF:DateTimeOriginal",
                "QuickTime:CreateDate",
            ]
            if key in found
        ]
        logger.debug("Raw dates found for %s: %s", source_path, raw_datetimes)
        possible_datetimes = [
            raw_datetime for raw_datetime in raw_datetimes
            if raw_datetime is not None
        ]
        if not possible_datetimes:
            # TODO: do heuristic on path if exiftool fails
            pass
        if possible_datetimes:
            logger.debug("Date times matched for %s: %s", source_path, possible_datetimes)
            confirmed_datetime = possible_datetimes[0]
            # build file name from datetime
            file_directory = Path(destination, f"{confirmed_datetime.year}", f"{confirmed_datetime.month}".zfill(2))
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
            file_directory.mkdir(parents=True)
        shutil.copy2(source_path, Path(file_directory, file_name))
        # TODO: update with exiftool to match calculated date


def organize_media_chunk(destination, checksums):
    with exiftool.ExifToolHelper() as helper:
        # TODO: maybe make this unique across script invocations?
        process_id = threading.get_ident()
        logger.info("Processing chunk with process %s", process_id)
        organize_media(process_id, destination, checksums, helper)


def main():
    parser = argparse.ArgumentParser(
        description='Manipulate a given media directory'
    )
    parser.add_argument(
        'action', choices=['deduplicate'], help='action for media directory'
    )
    parser.add_argument('source', help='directory containing all files to traverse')
    parser.add_argument('destination', help='destination directory for cleaned media')
    parser.add_argument('-p', '--process-total', type=int, default=4, help='number of parallel processes to use')

    args = parser.parse_args()

    media_directory = Path(args.source)
    destination = Path(args.destination)
    if not media_directory.exists():
        logger.info("Directory %s does not exist", media_directory)
        sys.exit(1)
    if not destination.exists():
        destination.mkdir(parents=True)
    checksums = get_media_checksums(media_directory)
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


if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get('LOG_LEVEL', logging.INFO))
    main()
