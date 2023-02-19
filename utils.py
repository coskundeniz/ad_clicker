import sys
import random
import subprocess
from pathlib import Path
from time import sleep
from typing import Optional

import requests
import undetected_chromedriver
from selenium.webdriver import ChromeOptions

from config import logger
from geolocation_db import GeolocationDB
from proxy import install_plugin


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/107.0.5304.101 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/107.0.5304.101 Mobile/15E148 Safari/604.1",
]


def get_random_user_agent_string() -> str:
    """Get random user agent

    :rtype: str
    :returns: User agent string
    """

    user_agent_string = random.choice(USER_AGENTS)

    logger.debug(f"user_agent: {user_agent_string}")

    return user_agent_string


def get_location(
    geolocation_db_client: GeolocationDB, proxy: str, auth: Optional[bool] = False
) -> tuple[float, float]:
    """Get latitude and longitude of ip address

    :type geolocation_db_client: GeolocationDB
    :param geolocation_db_client: GeolocationDB instance
    :type proxy: str
    :param proxy: Proxy to get geolocation
    :type auth: bool
    :param auth: Whether authentication is used or not for proxy
    :rtype: tuple
    :returns: (latitude, longitude) pair for the given proxy IP
    """

    if auth:
        response = requests.get(
            "https://ipv4.webshare.io/",
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
        )

        ip_address = response.text
    else:
        ip_address = proxy.split(":")[0]

    logger.info(f"Connecting with IP: {ip_address}")

    db_result = geolocation_db_client.query_geolocation(ip_address)

    if db_result:
        latitude, longitude = db_result
        logger.debug(f"Cached latitude and longitude for {ip_address}: ({latitude}, {longitude})")

        return float(latitude), float(longitude)

    else:
        retry_count = 0

        while retry_count < 5:

            try:
                response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=2).json()
                latitude, longitude = response.get("latitude"), response.get("longitude")

                if not (latitude or longitude):
                    # try a different api
                    response = requests.get(
                        f"https://geolocation-db.com/json/{ip_address}", timeout=2
                    ).json()
                    latitude, longitude = response.get("latitude"), response.get("longitude")

                    if latitude == "Not found":
                        latitude = longitude = None

                if latitude and longitude:
                    logger.debug(
                        f"Latitude and longitude for {ip_address}: ({latitude}, {longitude})"
                    )
                    geolocation_db_client.save_geolocation(ip_address, latitude, longitude)

                    return latitude, longitude

            except requests.RequestException as exp:
                logger.error(exp)

            logger.debug(
                f"Couldn't find latitude and longitude for {ip_address}! Retrying after a second..."
            )

            retry_count += 1
            sleep(1)

        if not (latitude or longitude):
            return (None, None)


def get_installed_chrome_version() -> int:
    """Get major version for the Chrome installed on the system

    :rtype: int
    :returns: Chrome major version
    """

    major_version = None

    try:
        if sys.platform == "win32":
            chrome_exe_path = undetected_chromedriver.find_chrome_executable()
            version_command = (
                f"wmic datafile where name='{chrome_exe_path}' get Version /value".replace(
                    "\\", "\\\\"
                )
            )
            chrome_version = subprocess.check_output(version_command, shell=True)
            major_version = int(chrome_version.decode("utf-8").strip().split(".")[0].split("=")[1])
        else:
            result = subprocess.run(["google-chrome", "--version"], capture_output=True)
            major_version = int(str(result.stdout).split(" ")[-2].split(".")[0])

        logger.debug(f"Installed Chrome version: {major_version}")

    except subprocess.SubprocessError:
        logger.error("Failed to get Chrome version! Latest version will be used.")

    return major_version


def get_queries(query_file: Path) -> list[str]:
    """Get queries from file

    :type query_file: Path
    :param query_file: File containing queries
    :rtype: list
    :returns: List of queries
    """

    filepath = Path(query_file)

    if not filepath.exists():
        raise SystemExit(f"Couldn't find queries file: {filepath}")

    with open(filepath) as queryfile:
        queries = queryfile.read().splitlines()

    return queries


def create_webdriver(proxy: str, auth: bool, headless: bool) -> undetected_chromedriver.Chrome:
    """Create Selenium Chrome webdriver instance

    :type proxy: str
    :param proxy: Proxy to use in ip:port or user:pass@host:port format
    :type auth: bool
    :param auth: Whether authentication is used or not for proxy
    :type headless: bool
    :param headless: Whether to use headless browser
    :rtype: undetected_chromedriver.Chrome
    :returns: Selenium Chrome webdriver instance
    """

    geolocation_db_client = GeolocationDB()

    user_agent_str = get_random_user_agent_string()

    chrome_options = ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(f"--user-agent={user_agent_str}")

    if headless:
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

    chrome_version = get_installed_chrome_version()

    if proxy:

        logger.info(f"Using proxy: {proxy}")

        if auth:

            if "@" not in proxy or proxy.count(":") != 2:
                raise ValueError(
                    "Invalid proxy format! Should be in 'username:password@host:port' format"
                )

            username, password = proxy.split("@")[0].split(":")
            host, port = proxy.split("@")[1].split(":")

            install_plugin(chrome_options, host, int(port), username, password)

        else:
            chrome_options.add_argument(f"--proxy-server={proxy}")

        driver = undetected_chromedriver.Chrome(
            version_main=chrome_version,
            options=chrome_options,
            headless=headless,
        )

        # set geolocation of the browser according to IP address
        accuracy = 90
        lat, long = get_location(geolocation_db_client, proxy, auth)

        if lat and long:
            driver.execute_cdp_cmd(
                "Emulation.setGeolocationOverride",
                {"latitude": lat, "longitude": long, "accuracy": accuracy},
            )

    else:
        driver = undetected_chromedriver.Chrome(
            version_main=chrome_version, options=chrome_options, headless=headless
        )

    return driver
