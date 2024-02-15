"""
BAŞLANGIÇ

Doğanın bana verdiği bu ödülden
Çıldırıp yitmemek için
İki insan gibi kaldım
Birbiriyle konuşan iki insan

            -- Edip Cansever
"""

import random
import traceback
from argparse import ArgumentParser

from config import logger, update_log_formats
from proxy import get_proxies
from utils import create_webdriver
from search_controller import SearchController


__author__ = "Coşkun Deniz <coskun.denize@gmail.com>"


def get_arg_parser() -> ArgumentParser:
    """Get argument parser

    :rtype: ArgumentParser
    :returns: ArgumentParser object
    """

    arg_parser = ArgumentParser()
    arg_parser.add_argument("-q", "--query", help="Search query")
    arg_parser.add_argument(
        "-l",
        "--max_scroll_limit",
        default=0,
        type=int,
        help="Number of maximum scrolls on the search results page",
    )
    arg_parser.add_argument("--headless", action="store_true", help="Use headless browser")
    arg_parser.add_argument(
        "-p",
        "--proxy",
        help="""Use the given proxy in "ip:port" or "username:password@host:port" format""",
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
        "-e",
        "--excludes",
        help="Exclude the ads that contain given words in url or title",
    )
    arg_parser.add_argument("--id", help="Browser id for multiprocess run")
    arg_parser.add_argument("--incognito", action="store_true", help="Run in incognito mode")
    arg_parser.add_argument("--poem", help="Get the poem for the given module")

    return arg_parser


def get_poem(module_name: str) -> None:
    """Get the poem for the given module

    :type module_name: str
    :param module_name: Module name without .py extension
    """

    import sys
    import importlib

    module = module_name if module_name != "ad_clicker" else __name__

    if module in ["run_ad_clicker", "run_in_loop"]:
        importlib.import_module(module)

    try:
        module_doc = sys.modules[module].__doc__
        print(f"{module_doc}\n")

    except KeyError:
        logger.error("No module exists with this name!")


def main():
    """Entry point for the tool"""

    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()

    if args.poem:
        get_poem(args.poem)
        raise SystemExit()

    if args.id:
        update_log_formats(args.id)

    if not args.query:
        logger.error("Run with search query!")
        arg_parser.print_help()
        raise SystemExit()

    if args.proxy:
        proxy = args.proxy
    elif args.proxy_file:
        proxies = get_proxies(args.proxy_file)
        logger.debug(f"Proxies: {proxies}")

        proxy = random.choice(proxies)
    else:
        proxy = None

    driver = create_webdriver(proxy, args.auth, args.headless, args.incognito)

    search_controller = None

    try:
        search_controller = SearchController(
            driver, args.query, args.max_scroll_limit, args.excludes
        )
        ads = search_controller.search_for_ads()

        if not ads:
            logger.info("No ads in the search results!")
        else:
            logger.info(f"Found {len(ads)} ads")
            search_controller.click_ads(ads)

    except Exception as exp:
        logger.error("Exception occurred. See the details in the log file.")

        message = str(exp).split("\n")[0]
        logger.debug(f"Exception: {message}")
        details = traceback.format_tb(exp.__traceback__)
        logger.debug(f"Exception details: \n{''.join(details)}")

        logger.debug(f"Exception cause: {exp.__cause__}") if exp.__cause__ else None

    finally:
        if search_controller:
            search_controller.end_search()


if __name__ == "__main__":

    main()
