from time import sleep
from typing import Optional, Union

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxProfile, ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver

from config import logger
from translations import contains_ad


ProxySetup = Optional[Union[ChromeOptions, FirefoxProfile]]
AdList = list[tuple[selenium.webdriver.remote.webelement.WebElement, str]]


class SearchController:
    """Search controller for ad clicker

    :type query: str
    :param query: Search query
    :type ad_visit_time: int
    :param ad_visit_time: Number of seconds to wait on the ad page
    :type headless: bool
    :param headless: Whether to use headless browser
    """

    URL = "https://www.google.com"
    SEARCH_INPUT = (By.NAME, "q")
    RESULTS_CONTAINER = (By.ID, "result-stats")
    COOKIE_DIALOG = (By.CSS_SELECTOR, "div[role='dialog']")
    COOKIE_ACCEPT_BUTTON = (By.TAG_NAME, "button")
    TOP_ADS_CONTAINER = (By.ID, "tads")
    AD_RESULTS = (By.CSS_SELECTOR, "div > a")
    AD_LANG_TEXT = (By.CSS_SELECTOR, "div:last-child > span:first-child")

    def __init__(self, query: str, ad_visit_time: int, headless: bool) -> None:

        self._search_query = query
        self._ad_visit_time = ad_visit_time
        self._headless = headless

        self._driver = self._create_driver()
        self._load()

    def search_for_ads(self):
        """Start search for the given query and return ads if any

        :rtype: list
        :returns: List of (ad, ad_link) tuples
        """

        logger.info(f"Starting search for '{self._search_query}'")

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

    def _create_driver(self) -> selenium.webdriver:
        """Create Selenium Chrome webdriver instance

        :rtype: selenium.webdriver
        :returns: Selenium webdriver instance
        """

        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")

        if self._headless:
            chrome_options.add_argument("--window-size=1920,1080")

        driver = undetected_chromedriver.Chrome(options=chrome_options, headless=self._headless)

        return driver

    def _load(self) -> None:
        """Load Google main page"""

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
