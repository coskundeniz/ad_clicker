from argparse import ArgumentParser

from config import logger
from search_controller import SearchController


def get_arg_parser() -> ArgumentParser:
    """Get argument parser

    :rtype: ArgumentParser
    :returns: ArgumentParser object
    """

    arg_parser = ArgumentParser()
    arg_parser.add_argument("-q", "--query", help="Search query")
    arg_parser.add_argument(
        "-t",
        "--visittime",
        default=4,
        type=int,
        dest="ad_visit_time",
        help="Number of seconds to wait on the ad page opened",
    )
    arg_parser.add_argument("--headless", action="store_true", help="Use headless browser")

    return arg_parser


def main():
    """Entry point for the tool"""

    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()

    if not args.query:
        logger.error("Run with search query!")
        arg_parser.print_help()
        raise SystemExit()

    search_controller = SearchController(args.query, args.ad_visit_time, args.headless)
    ads = search_controller.search_for_ads()

    if not ads:
        logger.info("No ads in the search results!")
    else:
        logger.info(f"Found {len(ads)} ads")
        search_controller.click_ads(ads)
        search_controller.end_search()


if __name__ == "__main__":

    main()
