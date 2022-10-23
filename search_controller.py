from time import sleep
from typing import Optional, Union

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxProfile, ChromeOptions
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)
from webdriver_setup import get_webdriver_for


from config import logger
from translations import contains_ad


ProxySetup = Optional[Union[ChromeOptions, FirefoxProfile]]
AdList = list[tuple[selenium.webdriver.remote.webelement.WebElement, str]]


class SearchController:
    """Search controller for ad clicker

    :type query: str
    :param query: Search query
    :type browser: str
    :param browser: Browser to use
    :type ad_visit_time: int
    :param ad_visit_time: Number of seconds to wait on the ad page
    :type use_tor: bool
    :param use_tor: Whether to use tor network or not
    """

    URL = "https://www.google.com"
    SEARCH_INPUT = (By.NAME, "q")
    RESULTS_CONTAINER = (By.ID, "result-stats")
    COOKIE_DIALOG = (By.CSS_SELECTOR, "div[role='dialog']")
    COOKIE_ACCEPT_BUTTON = (By.TAG_NAME, "button")
    TOP_ADS_CONTAINER = (By.ID, "tads")
    AD_RESULTS = (By.CSS_SELECTOR, "div > a")
    AD_LANG_TEXT = (By.CSS_SELECTOR, "div:last-child > span:first-child")

    def __init__(self, query: str, browser: str, ad_visit_time: int, use_tor: bool) -> None:

        self._search_query = query
        self._ad_visit_time = ad_visit_time
        self._use_tor = use_tor

        self._driver = self._create_driver(browser.lower())
        self._load()

    def search_for_ads(self):
        """Start search for the given query and return ads if any

        :rtype: list
        :returns: List of (ad, ad_link) tuples
        """

        logger.info(f"Starting search for '{self._search_query}'")

        self._close_cookie_dialog()

        search_input_box = self._driver.find_element(*self.SEARCH_INPUT)
        search_input_box.send_keys(self._search_query, Keys.ENTER)

        ad_links = []

        try:
            wait = WebDriverWait(self._driver, timeout=10)
            results_loaded = wait.until(EC.presence_of_element_located(self.RESULTS_CONTAINER))

            if results_loaded:
                logger.info("Getting ad links...")
                ad_links = self._get_ad_links()

        except TimeoutException:
            logger.error("Timed out waiting for results!")
            self.end_search()

        return ad_links

    def click_ads(self, ads: AdList) -> None:
        """Click ads found

        :type ads: AdList
        :param ads: List of (ad, ad_link) tuples
        """

        # store the ID of the original window
        original_window_handle = self._driver.current_window_handle

        for ad in ads:
            ad_link_element = ad[0]
            ad_link = ad[1]
            logger.info(f"Clicking {ad_link}...")

            # open link in a different tab
            ad_link_element.send_keys(Keys.CONTROL + Keys.RETURN)

            for window_handle in self._driver.window_handles:
                if window_handle != original_window_handle:
                    self._driver.switch_to.window(window_handle)
                    sleep(self._ad_visit_time)
                    self._driver.close()
                    break

            # go back to original window
            self._driver.switch_to.window(original_window_handle)
            sleep(1)

            # scroll the page to avoid elements remain outside of the view
            self._driver.execute_script("arguments[0].scrollIntoView(true);", ad_link_element)

    def end_search(self) -> None:
        """Close the browsers"""

        if self._driver:
            # delete all cookies before quitting
            self._driver.delete_all_cookies()
            self._driver.quit()

    def _create_driver(self, browser: str) -> selenium.webdriver:
        """Create Selenium webdriver instance for the given browser

        Setup proxy if the browser is Firefox or Chrome

        :type browser: str
        :param browser: Browser name
        :rtype: selenium.webdriver
        :returns: Selenium webdriver instance
        """

        try:
            proxy = self._setup_proxy(browser) if self._use_tor else None

            if browser == "firefox":
                driver = get_webdriver_for(browser, firefox_profile=proxy)
            elif browser == "chrome":
                driver = get_webdriver_for(browser, chrome_options=proxy)
            else:
                driver = get_webdriver_for(browser)

        except ValueError:
            logger.error(f"{browser} is not installed on your system!")
            raise SystemExit()

        return driver

    def _setup_proxy(self, browser: str) -> ProxySetup:
        """Setup proxy for Firefox or Chrome

        :type browser: str
        :param browser: Browser name
        :rtype: ChromeOptions or FirefoxProfile
        :returns: Proxy settings
        """

        host = "127.0.0.1"
        port = "9050"

        if browser == "firefox":
            firefox_profile = FirefoxProfile()
            # Direct = 0, Manual = 1, PAC = 2, AUTODETECT = 4, SYSTEM = 5
            firefox_profile.set_preference("network.proxy.type", 1)
            firefox_profile.set_preference("network.proxy.socks", host)
            firefox_profile.set_preference("network.proxy.socks_port", int(port))
            firefox_profile.update_preferences()

            return firefox_profile

        elif browser == "chrome":
            proxy = f"socks5://{host}:{port}"
            chrome_options = ChromeOptions()
            chrome_options.add_argument(f"--proxy-server={proxy}")

            return chrome_options

        else:
            logger.info(f"No proxy setting was done for {browser}")

    def _load(self) -> None:
        """Load Google main page"""

        self._driver.maximize_window()
        self._driver.get(self.URL)

    def _get_ad_links(self) -> AdList:
        """Extract ad links to click

        :rtype: AdList
        :returns: List of (ad, ad_link) tuples
        """

        ad_links = []

        try:
            ads_container = self._driver.find_element(*self.TOP_ADS_CONTAINER)
        except NoSuchElementException as exp:
            logger.debug(exp)
            return ad_links

        ads = ads_container.find_elements(*self.AD_RESULTS)

        # clean sublinks
        ads = [ad_link for ad_link in ads if ad_link.get_attribute("data-pcu")]

        for ad in ads:
            ad_text_element = ad.find_element(*self.AD_LANG_TEXT)
            ad_text = ad_text_element.text.lower()

            if contains_ad(ad_text):
                logger.info("======= Found an Ad =======")
                ad_link = ad.get_attribute("href")
                logger.debug(f"Ad Link: {ad_link}")
                ad_links.append((ad, ad_link))

        return ad_links

    def _close_cookie_dialog(self) -> None:
        """If cookie dialog is opened, close it by accepting"""

        try:
            cookie_dialog = self._driver.find_element(*self.COOKIE_DIALOG)
            accept_button = cookie_dialog.find_elements(*self.COOKIE_ACCEPT_BUTTON)[-2]
            accept_button.click()
            sleep(1)

        except (NoSuchElementException, ElementNotInteractableException):
            pass
