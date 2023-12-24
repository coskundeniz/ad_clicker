"""
HAYAT BÖYLE ZATEN

Bu evin bir köpeği vardı;
Kıvır kıvırdı, adı Çinçon'du, öldü.
Bir de kedisi vardı: Maviş,
Kayboldu.
Evin kızı gelin oldu,
Küçük Bey sınıfı geçti.
Daha böyle acı, tatlı
Neler oldu bir yıl içinde!
Oldu ya, olanların hepsi böyle...
Hayat böyle zaten!..

                        -- Orhan Veli
"""

import os
import sys
import random
from pathlib import Path
from time import sleep
from typing import Optional

import requests
import undetected_chromedriver

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5735.57 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.5735.57 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5735.57 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.5735.57 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/107.0.5304.101 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/107.0.5304.101 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1"
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

    proxies_header = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    ip_address = ""

    if auth:
        for cycle in range(2):
            try:
                response = requests.get("https://api.ipify.org", proxies=proxies_header)
                ip_address = response.text

                if not ip_address:
                    raise Exception("Failed with https://api.ipify.org")

                break

            except Exception as exp:
                logger.debug(exp)

                try:
                    logger.debug("Trying with ipv4.webshare.io...")
                    response = requests.get(
                        "https://ipv4.webshare.io/", proxies=proxies_header, timeout=5
                    )
                    ip_address = response.text

                    if not ip_address:
                        raise Exception("Failed with https://ipv4.webshare.io")

                    break

                except Exception as exp:
                    logger.debug(exp)

                    try:
                        logger.debug("Trying with ipconfig.io...")
                        response = requests.get(
                            "https://ipconfig.io/json", proxies=proxies_header, timeout=5
                        )
                        ip_address = response.json().get("ip")

                        if not ip_address:
                            raise Exception("Failed with https://ipconfig.io/json")

                        break

                    except Exception as exp:
                        logger.debug(exp)

                        if cycle == 1:
                            break

                        logger.debug("Request will be resend after 60 seconds")
                        sleep(60)
    else:
        ip_address = proxy.split(":")[0]

    if not ip_address:
        logger.info(f"Couldn't verify IP address for {proxy}!")
        logger.info("Geolocation won't be set")
        return (None, None)

    logger.info(f"Connecting with IP: {ip_address}")

    db_result = geolocation_db_client.query_geolocation(ip_address)

    latitude = None
    longitude = None

    if db_result:
        latitude, longitude = db_result
        logger.debug(f"Cached latitude and longitude for {ip_address}: ({latitude}, {longitude})")

        return float(latitude), float(longitude)

    else:
        retry_count = 0
        max_retry_count = 5
        sleep_seconds = 5

        while retry_count < max_retry_count:
            try:
                response = requests.get(
                    f"https://ipapi.co/{ip_address}/json/", proxies=proxies_header, timeout=5
                )
                latitude, longitude = (
                    response.json().get("latitude"),
                    response.json().get("longitude"),
                )

                if not (latitude and longitude):
                    raise Exception("Failed with https://ipapi.co")

                break
            except Exception as exp:
                logger.debug(exp)
                logger.debug("Continue with ifconfig.co")

                try:
                    response = requests.get(
                        "https://ifconfig.co/json", proxies=proxies_header, timeout=5
                    )
                    latitude, longitude = (
                        response.json().get("latitude"),
                        response.json().get("longitude"),
                    )

                    if not (latitude and longitude):
                        raise Exception("Failed with https://ifconfig.co/json")

                    break
                except Exception as exp:
                    logger.debug(exp)
                    logger.debug("Continue with ipconfig.io")

                    try:
                        response = requests.get(
                            "https://ipconfig.io/json/", proxies=proxies_header, timeout=5
                        )
                        latitude, longitude = (
                            response.json()["latitude"],
                            response.json()["longitude"],
                        )

                        if not (latitude and longitude):
                            raise Exception("Failed with https://ipconfig.io/json")

                        break
                    except Exception as exp:
                        logger.debug(exp)
                        logger.error(
                            f"Couldn't find latitude and longitude for {ip_address}! "
                            f"Retrying after {sleep_seconds} seconds..."
                        )

                        retry_count += 1
                        sleep(sleep_seconds)
                        sleep_seconds *= 2

        if latitude and longitude:
            logger.debug(f"Latitude and longitude for {ip_address}: ({latitude}, {longitude})")
            geolocation_db_client.save_geolocation(ip_address, latitude, longitude)

            return (latitude, longitude)
        else:
            logger.error(f"Couldn't find latitude and longitude for {ip_address}!")
            return (None, None)


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

    with open(filepath, encoding="utf-8") as queryfile:
        queries = [
            query.strip().replace("'", "").replace('"', "")
            for query in queryfile.read().splitlines()
        ]

    return queries


def create_webdriver(
    proxy: str, auth: bool, headless: bool, incognito: Optional[bool] = False
) -> undetected_chromedriver.Chrome:
    """Create Selenium Chrome webdriver instance

    :type proxy: str
    :param proxy: Proxy to use in ip:port or user:pass@host:port format
    :type auth: bool
    :param auth: Whether authentication is used or not for proxy
    :type headless: bool
    :param headless: Whether to use headless browser
    :type incognito: bool
    :param incognito: Whether to run in incognito mode
    :rtype: undetected_chromedriver.Chrome
    :returns: Selenium Chrome webdriver instance
    """

    geolocation_db_client = GeolocationDB()

    user_agent_str = get_random_user_agent_string()

    chrome_options = undetected_chromedriver.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--deny-permission-prompts")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-service-autorun")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"--user-agent={user_agent_str}")

    # disable these features for saving some proxy bandwidth
    optimization_features = [
        "OptimizationGuideModelDownloading",
        "OptimizationHintsFetching",
        "OptimizationTargetPrediction",
        "OptimizationHints",
        "Translate",
        "DownloadBubble",
        "DownloadBubbleV2",
    ]
    chrome_options.add_argument(f"--disable-features={','.join(optimization_features)}")

    # disable WebRTC IP tracking
    webrtc_preferences = {
        "webrtc.ip_handling_policy": "disable_non_proxied_udp",
        "webrtc.multiple_routes_enabled": False,
        "webrtc.nonproxied_udp_enabled": False,
    }
    chrome_options.add_experimental_option("prefs", webrtc_preferences)

    if incognito:
        chrome_options.add_argument("--incognito")

    if headless:
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

    multi_browser_flag_file = Path(".MULTI_BROWSERS_IN_USE")
    multi_procs_enabled = multi_browser_flag_file.exists()
    driver_exe_path = None

    if multi_procs_enabled:
        driver_exe_path = _get_driver_exe_path()

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
            driver_executable_path=(
                driver_exe_path if multi_procs_enabled and Path(driver_exe_path).exists() else None
            ),
            options=chrome_options,
            headless=headless,
            user_multi_procs=multi_procs_enabled,
        )

        # set geolocation of the browser according to IP address
        accuracy = 90
        lat, long = get_location(geolocation_db_client, proxy, auth)

        if lat and long:
            driver.execute_cdp_cmd(
                "Emulation.setGeolocationOverride",
                {"latitude": lat, "longitude": long, "accuracy": accuracy},
            )

            response = requests.get(
                f"http://timezonefinder.michelfe.it/api/0_{long}_{lat}", timeout=5
            )

            if response.status_code == 200:
                timezone = response.json()["tz_name"]
                logger.debug(f"Timezone of {proxy.split('@')[1] if auth else proxy}: {timezone}")
                driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": timezone})

    else:
        driver = undetected_chromedriver.Chrome(
            driver_executable_path=(
                driver_exe_path if multi_procs_enabled and Path(driver_exe_path).exists() else None
            ),
            options=chrome_options,
            headless=headless,
            user_multi_procs=multi_procs_enabled,
        )

    return driver


def _get_driver_exe_path() -> str:
    """Get the path for the chromedriver executable to avoid downloading and patching each time

    :rtype: str
    :returns: Absoulute path of the chromedriver executable
    """

    platform = sys.platform
    prefix = "undetected"
    exe_name = "chromedriver%s"

    if platform.endswith("win32"):
        exe_name %= ".exe"
    if platform.endswith(("linux", "linux2")):
        exe_name %= ""
    if platform.endswith("darwin"):
        exe_name %= ""

    if platform.endswith("win32"):
        dirpath = "~/appdata/roaming/undetected_chromedriver"
    elif "LAMBDA_TASK_ROOT" in os.environ:
        dirpath = "/tmp/undetected_chromedriver"
    elif platform.startswith(("linux", "linux2")):
        dirpath = "~/.local/share/undetected_chromedriver"
    elif platform.endswith("darwin"):
        dirpath = "~/Library/Application Support/undetected_chromedriver"
    else:
        dirpath = "~/.undetected_chromedriver"

    driver_exe_folder = os.path.abspath(os.path.expanduser(dirpath))
    driver_exe_path = os.path.join(driver_exe_folder, "_".join([prefix, exe_name]))

    return driver_exe_path
