#!/usr/bin/env python3
import os
from pathlib import Path, PurePath
from collections import defaultdict
import argparse
import sys
import logging
import hashlib
import shutil
from datetime import datetime

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


def get_photo_checksums(directory_path, checksums=None):
    if checksums is None:
        checksums = defaultdict(set)
    # traverse directory
    for cur_path in directory_path.iterdir():
        if cur_path.is_file():
            # for each file detected as a photo
            file_type = magic.from_file(cur_path, mime=True)
            logger.debug(
                "Detected file type %s from path %s", file_type, cur_path,
            )
            if file_type == 'image/jpeg':
                # store checksum with set of paths
                path_checksum = checksum(cur_path)
                checksums[path_checksum].add(cur_path)
            elif file_type == 'video/quicktime':
                # FIXME: handle videos too
                pass
        elif cur_path.is_dir():
            get_photo_checksums(cur_path, checksums=checksums)
    return checksums


def organize_photos(checksums, helper, destination):
    # run exiftool on cleaned photo paths
    for checksum, paths in checksums.items():
        metadata = helper.get_metadata(paths)
        source_path = paths.pop()
        logger.info("Processing %s", source_path)
        # possible metadata keys for change date:
        # EXIF:DateTimeOriginal
        # EXIF:CreateDate
        # EXIF:ModifyDate
        raw_datetimes = [
            parse_datetime(found[key])
            for found in metadata
            for key in [
                "EXIF:DateTimeOriginal",
            ]
            if key in found
        ]
        logger.debug("Raw dates found for %s: %s", source_path, raw_datetimes)
        possible_datetimes = [
            raw_datetime for raw_datetime in raw_datetimes
            if raw_datetime is not None
        ]
        # TODO: determine file extension from File:FileType or existing extension
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
                f"{confirmed_datetime.second:02}.jpg"
            )
        else:
            logger.debug("%s unsorted", source_path)
            file_directory = Path(destination, "Unsorted")
            file_name = source_path.name
        # copy path to organised destination
        if not file_directory.exists():
            file_directory.mkdir(parents=True)
        shutil.copy2(source_path, Path(file_directory, file_name))
        # TODO: update with exiftool to match calculated date


def main():
    parser = argparse.ArgumentParser(
        description='Manipulate a given photo directory'
    )
    parser.add_argument(
        'action', choices=['deduplicate'], help='action for photo directory'
    )
    parser.add_argument('source', help='directory containing all files to traverse')
    parser.add_argument('destination', help='destination directory for cleaned images')

    args = parser.parse_args()

    photo_directory = Path(args.source)
    destination = Path(args.destination)
    if not photo_directory.exists():
        logger.info("Directory %s does not exist", photo_directory)
        sys.exit(1)
    if not destination.exists():
        destination.mkdir(parents=True)
    checksums = get_photo_checksums(photo_directory)
    logger.info("Found %s unique checksums", len(checksums))
    # TODO: dedupe paths by checking byte equality
    with exiftool.ExifToolHelper() as helper:
        organize_photos(checksums, helper, destination)


if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get('LOG_LEVEL', logging.INFO))
    main()
