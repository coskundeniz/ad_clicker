"""
GELİRLİ ŞİİR

İstanbul'dan ayva da gelir, nar gelir,
Döndüm baktım, bir edalı yâr gelir,
Gelir desen dar gelir;
Gün aşırı alacaklılar gelir.
Anam anam,
Dayanamam,
Bu iş bana zor gelir.

                -- Orhan Veli
"""

import random
import traceback
import subprocess
import multiprocessing
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor, wait
from itertools import cycle
from pathlib import Path
from time import sleep
from typing import Optional

from config import logger
from proxy import get_proxies
from utils import get_queries


def get_arg_parser() -> ArgumentParser:
    """Get argument parser

    :rtype: ArgumentParser
    :returns: ArgumentParser object
    """

    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-qf",
        "--query_file",
        help="Read queries to search from the given file",
    )
    arg_parser.add_argument(
        "-pf",
        "--proxy_file",
        help="Select a proxy from the given file",
    )
    arg_parser.add_argument(
        "-l",
        "--max_scroll_limit",
        default=0,
        type=int,
        help="Number of maximum scrolls on the search results page",
    )
    arg_parser.add_argument(
        "-e",
        "--excludes",
        help="Exclude the ads that contain given words in url or title",
    )
    arg_parser.add_argument(
        "--auth",
        action="store_true",
        help="""Use proxy with username and password.
        If this is passed, proxy parameter should be in "username:password@host:port" format
        """,
    )
    arg_parser.add_argument(
        "-bc",
        "--browser_count",
        default=multiprocessing.cpu_count(),
        type=int,
        help="Maximum number of browsers to run concurrently",
    )
    arg_parser.add_argument(
        "-ms",
        "--multiprocess_style",
        default=1,
        type=int,
        help="""Style of the multiprocess run.
        1: single browser instance for each query (default)
        2: multiple browser instances for each query
        """,
    )
    arg_parser.add_argument("--incognito", action="store_true", help="Run in incognito mode")

    return arg_parser


def start_tool(
    browser_id: int,
    query: str,
    proxy: str,
    start_timeout: float,
    max_scroll_limit: int,
    auth: Optional[bool] = None,
    excludes: Optional[str] = None,
    incognito: Optional[bool] = False,
) -> None:
    """Start the tool

    :type browser_id: int
    :param browser_id: Browser id to separate instances in log for multiprocess runs
    :type query: str
    :param query: Search query
    :type proxy: str
    :param proxy: Proxy to use in ip:port or user:pass@host:port format
    :type start_timeout: float
    :param start_timeout: Start timeout to avoid race condition in driver patching
    :type max_scroll_limit: int
    :param max_scroll_limit: Number of maximum scrolls on the search results page
    :type auth: bool
    :param auth: Whether authentication is used or not for proxy
    :type excludes: str
    :param excludes: Words to exclude ads containing them in url or title
    :type incognito: bool
    :param incognito: Whether to run in incognito mode
    """

    sleep(start_timeout)

    command = ["python", "ad_clicker.py"]

    command.extend(["-q", query, "-p", proxy, "-l", str(max_scroll_limit)])

    if auth:
        command.append("--auth")

    command.extend(["--id", str(browser_id)])

    if excludes:
        command.extend(["-e", excludes])

    if incognito:
        command.append("--incognito")

    subprocess.run(command)


def main() -> None:

    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()

    multi_browser_flag_file = Path(".MULTI_BROWSERS_IN_USE")
    multi_browser_flag_file.unlink(missing_ok=True)

    MAX_WORKERS = args.browser_count

    if MAX_WORKERS > 1:
        logger.debug(f"Creating {multi_browser_flag_file} flag file...")
        multi_browser_flag_file.touch()

    if args.query_file:
        queries = get_queries(args.query_file)
        query = cycle(queries) if len(queries) <= MAX_WORKERS else iter(queries)
    else:
        raise SystemExit("Missing query file!")

    if args.proxy_file:
        proxies = get_proxies(args.proxy_file)
        random.shuffle(proxies)
        proxy = cycle(proxies) if len(proxies) <= MAX_WORKERS else iter(proxies)
    else:
        raise SystemExit("Missing proxy file!")

    logger.info(f"Running with {MAX_WORKERS} browser{'s' if MAX_WORKERS > 1 else ''}...")

    # 1st way - different query on each browser
    if args.multiprocess_style == 1:
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:

            futures = [
                executor.submit(
                    start_tool,
                    i,
                    next(query),
                    next(proxy),
                    i * 0.5,
                    args.max_scroll_limit,
                    args.auth,
                    args.excludes,
                    args.incognito,
                )
                for i in range(1, MAX_WORKERS + 1)
            ]

            # wait for all tasks to complete
            _, _ = wait(futures)

    # 2nd way - same query on each browser
    elif args.multiprocess_style == 2:

        for query in queries:

            proxies = get_proxies(args.proxy_file)
            random.shuffle(proxies)
            proxy = cycle(proxies)

            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:

                futures = [
                    executor.submit(
                        start_tool,
                        i,
                        query,
                        next(proxy),
                        i * 0.5,
                        args.max_scroll_limit,
                        args.auth,
                        args.excludes,
                        args.incognito,
                    )
                    for i in range(1, MAX_WORKERS + 1)
                ]

                # wait for all tasks to complete
                _, _ = wait(futures)

    else:
        logger.error("Invalid multiprocess style!")


if __name__ == "__main__":

    try:
        main()

    except Exception as exp:
        logger.error("Exception occurred. See the details in the log file.")

        message = str(exp).split("\n")[0]
        logger.debug(f"Exception: {message}")
        details = traceback.format_tb(exp.__traceback__)
        logger.debug(f"Exception details: \n{''.join(details)}")
