import psutil
import random
import subprocess
import multiprocessing
from itertools import cycle
from concurrent.futures import ProcessPoolExecutor, wait

from argparse import ArgumentParser
from pathlib import Path

from config import logger
from proxy import get_proxies
from utils import get_queries


def get_arg_parser() -> ArgumentParser:
    """Get argument parser

    :rtype: ArgumentParser
    :returns: ArgumentParser object
    """

    arg_parser = ArgumentParser()
    arg_parser.add_argument("-q", "--query", help="Search query")
    arg_parser.add_argument(
        "-p",
        "--proxy",
        help="""Use the given proxy in "ip:port" or "username:password@host:port" format""",
    )
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

    return arg_parser


def start_tool(browser_id, query, proxy, auth) -> None:
    """Start the tool

    :type browser_id: int
    :param browser_id: Browser id to separate instances in log for multiprocess runs
    :type query: str
    :param query: Search query
    :type proxy: str
    :param proxy: Proxy to use in ip:port or user:pass@host:port format
    :type auth: bool
    :param auth: Whether authentication is used or not for proxy
    """

    command = f"python {Path('ad_clicker.py').resolve()} -q '{query}' -p '{proxy}' {'--auth' if auth else ''} --id {browser_id}"
    subprocess.run(command, shell=True, check=True)


def cleanup() -> None:
    """If there is processes remained running, terminate them"""

    PROCESS_NAME = "ad_clicker"

    for process in psutil.process_iter():

        if (
            process.name() == "python"
            and PROCESS_NAME in process.cmdline()[1]
            and process.cmdline()[1] != "run_ad_clicker.py"
        ):
            logger.info(
                f"Terminating process: {' '.join(process.cmdline()[:2])}, PID: {process.pid}"
            )

            process.terminate()


def main():

    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()

    MAX_WORKERS = args.browser_count

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

    # 1st way - single browser instance for each query
    if args.multiprocess_style == 1:
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:

            futures = [
                executor.submit(start_tool, i, next(query), next(proxy), args.auth)
                for i in range(1, MAX_WORKERS + 1)
            ]

            # wait for all tasks to complete
            _, _ = wait(futures)

            cleanup()

    # 2nd way - multiple browser instances for each query
    elif args.multiprocess_style == 2:

        for query in queries:

            proxies = get_proxies(args.proxy_file)
            random.shuffle(proxies)
            proxy = cycle(proxies)

            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:

                futures = [
                    executor.submit(start_tool, i, query, next(proxy), args.auth)
                    for i in range(1, MAX_WORKERS + 1)
                ]

                # wait for all tasks to complete
                _, _ = wait(futures)

                cleanup()

    else:
        logger.error("Invalid multiprocess style!")


if __name__ == "__main__":

    main()
