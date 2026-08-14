#!/usr/bin/env python3
import argparse
import logging
import signal
import time
from http import HTTPStatus
from urllib.request import urlopen, Request

is_running = False


def on_shutdown(*_args, **_kwargs):
    global is_running
    is_running = False


def check_network(args):
    logging.info("Checking network")
    request = Request(args.ping_url, method="HEAD")
    try:
        with urlopen(request, timeout=5) as response_context:
            logging.info("Network check response status: %s", response_context.status)
            return response_context.status == HTTPStatus.OK
    except Exception:
        logging.exception("No internet access due to error")
        return False


def run():
    parser = argparse.ArgumentParser("Basic watchdog for internet access")
    parser.add_argument(
        "--watchdog-file",
        default="/dev/watchdog",
        help="The watchdog file to keep active.",
    )
    parser.add_argument(
        "--ping-url",
        default="https://www.google.com/",
        help="URL for checking internet access.",
    )
    parser.add_argument(
        "--check-gap-secs", default=30, type=int, help="Time between access checks."
    )
    parser.add_argument(
        "--grace-period-secs",
        default=300,
        type=int,
        help="Grace period before watchdog writes stop.",
    )
    parser.add_argument("--log-level", default="INFO", help="Log level for the script.")
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    global is_running
    is_running = True
    signal.signal(signal.SIGTERM, on_shutdown)
    signal.signal(signal.SIGINT, on_shutdown)

    grace_start = time.time()
    next_check_time = time.time()
    with open(args.watchdog_file, "w") as file_handle:
        while is_running:
            cur_time = time.time()
            if next_check_time < cur_time and check_network(args):
                next_check_time = cur_time + args.check_gap_secs
                grace_start = time.time()
                file_handle.write("1")
                file_handle.flush()
            elif grace_start > cur_time - args.grace_period_secs:
                file_handle.write("1")
                file_handle.flush()
            time.sleep(1)


if __name__ == "__main__":
    run()
