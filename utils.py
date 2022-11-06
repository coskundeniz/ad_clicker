import re
import random
import subprocess
from time import sleep
from typing import Optional

import requests
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem, Popularity, SoftwareType

from config import logger


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
]


def get_random_user_agent_string() -> str:
    """Get random user agent

    If returned value from random_user_agent package has Chrome version less than 90,
    choice user agent string from the values defined in USER_AGENTS list.

    :rtype: str
    :returns: User agent string
    """

    software_names = [SoftwareName.CHROME.value]
    operating_systems = [
        OperatingSystem.MAC.value,
        OperatingSystem.LINUX.value,
        OperatingSystem.WINDOWS.value,
    ]
    software_types = [SoftwareType.WEB_BROWSER.value, SoftwareType.APPLICATION.value]
    popularity = [Popularity.POPULAR.value, Popularity.COMMON.value, Popularity.AVERAGE.value]

    user_agent_rotator = UserAgent(
        software_names=software_names,
        operating_systems=operating_systems,
        software_types=software_types,
        popularity=popularity,
        limit=1000,
    )
    user_agents = user_agent_rotator.get_user_agents()
    selected_versions = []

    for item in user_agents:
        user_agent_str = item["user_agent"]

        if re.search("Chrome\/\s*v*(\d+)", user_agent_str):
            major_version = int(re.search("Chrome\/\s*v*(\d+)", user_agent_str).group(1))

            if major_version > 70:
                selected_versions.append((user_agent_str, major_version))

    if selected_versions:
        user_agent_string, chrome_version = sorted(
            selected_versions, key=lambda x: x[1], reverse=True
        )[0]

        if chrome_version < 90:
            user_agent_string = random.choice(USER_AGENTS)

    logger.debug(f"user_agent: {user_agent_string}")

    return user_agent_string


def get_location(proxy: str, auth: Optional[bool] = False) -> tuple[float, float]:
    """Get latitude and longitude of ip address

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

        logger.info(f"Connecting with IP: {ip_address}")
    else:
        ip_address = proxy.split(":")[0]

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
                logger.debug(f"Latitude and longitude for {ip_address}: ({latitude}, {longitude})")
                return latitude, longitude

        except requests.RequestException as exp:
            logger.error(exp)

        logger.error("Couldn't find latitude and longitude! Retrying after a second...")
        retry_count += 1
        sleep(1)


def get_installed_chrome_version() -> int:
    """Get major version for the Chrome installed on the system

    :rtype: int
    :returns: Chrome major version
    """

    major_version = None

    try:
        result = subprocess.run(["google-chrome", "--version"], capture_output=True)

        major_version = int(str(result.stdout).split(" ")[-2].split(".")[0])

        logger.debug(f"Installed Chrome version: {major_version}")

    except subprocess.SubprocessError:
        logger.error("Failed to get Chrome version! Latest version will be used.")

    return major_version
