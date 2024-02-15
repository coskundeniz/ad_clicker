"""
Yavaş Yavaş Ölürler

Yavaş yavaş ölürler
Seyahat etmeyenler.
Yavaş yavaş ölürler
Okumayanlar, müzik dinlemeyenler,
Vicdanlarında hoşgörüyü barındıramayanlar.
Yavaş yavaş ölürler
Alışkanlıklarına esir olanlar,
Her gün aynı yolları yürüyenler,
Ufuklarını genişletmeyen ve değiştirmeyenler,
Elbiselerinin rengini değiştirme riskine bile
girmeyenler,
Bir yabancı ile konuşmayanlar.
Yavaş yavaş ölürler
Heyecanlardan kaçınanlar,
Tamir edilen kırık kalplerin gözlerindeki pırıltıyı
görmek istemekten kaçınanlar.
Yavaş yavaş ölürler
Aşkta veya işte bedbaht olup yön değiştirmeyenler,
Rüyalarını gerçekleştirmek için risk almayanlar,
Hayatlarında bir kez dahi mantıklı tavsiyelerin
dışına çıkmamış olanlar.

                                -- Pablo Neruda
"""

import traceback
import subprocess
import multiprocessing
from argparse import ArgumentParser
from time import sleep

from config import logger


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
    arg_parser.add_argument(
        "-wt",
        "--wait_time",
        default=60,
        type=int,
        help="Number of seconds to wait between runs",
    )
    arg_parser.add_argument("--incognito", action="store_true", help="Run in incognito mode")

    return arg_parser


def main() -> None:

    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()

    if not args.query_file:
        raise SystemExit("Missing query file!")

    if not args.proxy_file:
        raise SystemExit("Missing proxy file!")

    command = ["python", "run_ad_clicker.py"]

    command.extend(
        ["-qf", args.query_file, "-pf", args.proxy_file, "-l", str(args.max_scroll_limit)]
    )

    if args.auth:
        command.append("--auth")

    if args.excludes:
        command.extend(["-e", args.excludes])

    if args.browser_count:
        command.extend(["-bc", str(args.browser_count)])

    if args.incognito:
        command.append("--incognito")

    command.extend(["-ms", str(args.multiprocess_style)])

    while True:
        subprocess.run(command)

        logger.info(f"Sleeping {args.wait_time} seconds...")
        sleep(args.wait_time)


if __name__ == "__main__":

    try:
        main()
    except Exception as exp:
        logger.error("Exception occurred. See the details in the log file.")
        message = str(exp).split("\n")[0]
        logger.debug(f"Exception: {message}")
        details = traceback.format_tb(exp.__traceback__)
        logger.debug(f"Exception details: \n{''.join(details)}")
