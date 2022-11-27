import random
from time import sleep

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)

from config import logger


AdList = list[tuple[selenium.webdriver.remote.webelement.WebElement, str, str]]


class SearchController:
    """Search controller for ad clicker

    :type driver: selenium.webdriver
    :param driver: Selenium Chrome webdriver instance
    :type query: str
    :param query: Search query
    :type ad_visit_time: int
    :param ad_visit_time: Number of seconds to wait on the ad page
    """

    URL = "https://www.google.com"

    SEARCH_INPUT = (By.NAME, "q")
    RESULTS_CONTAINER = (By.ID, "appbar")
    COOKIE_DIALOG = (By.CSS_SELECTOR, "div[role='dialog']")
    COOKIE_ACCEPT_BUTTON = (By.TAG_NAME, "button")
    TOP_ADS_CONTAINER = (By.ID, "tads")
    BOTTOM_ADS_CONTAINER = (By.ID, "tadsb")
    AD_RESULTS = (By.CSS_SELECTOR, "div > a")
    AD_TITLE = (By.CSS_SELECTOR, "div[role='heading']")

    def __init__(self, driver: selenium.webdriver, query: str, ad_visit_time: int) -> None:

        self._driver = driver
        self._ad_visit_time = ad_visit_time
        self._search_query, self._filter_words = self._process_query(query)

        self._load()

    def search_for_ads(self):
        """Start search for the given query and return ads if any

        :rtype: list
        :returns: List of (ad, ad_link, ad_title) tuples
        """

        logger.info(f"Starting search for '{self._search_query}'")

        self._close_cookie_dialog()

        search_input_box = self._driver.find_element(*self.SEARCH_INPUT)
        search_input_box.send_keys(self._search_query, Keys.ENTER)

        # sleep after entering search keyword by randomly selected amount
        # between 0.5 and 3 seconds
        sleep(random.choice([0.5, 3, 1, 1.5, 2, 2.5]))

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
        :param ads: List of (ad, ad_link, ad_title) tuples
        """

        # store the ID of the original window
        original_window_handle = self._driver.current_window_handle

        for ad in ads:
            ad_link_element = ad[0]
            ad_link = ad[1]
            ad_title = ad[2]
            logger.info(f"Clicking to [{ad_title}]({ad_link})...")

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

    def _load(self) -> None:
        """Load Google main page"""

        self._driver.get(self.URL)

    def _get_ad_links(self) -> AdList:
        """Extract ad links to click

        :rtype: AdList
        :returns: List of (ad, ad_link, ad_title) tuples
        """

        ads = []

        while not self._is_scroll_at_the_end():
            try:
                top_ads_containers = self._driver.find_elements(*self.TOP_ADS_CONTAINER)
                for ad_container in top_ads_containers:
                    ads.extend(ad_container.find_elements(*self.AD_RESULTS))

            except NoSuchElementException:
                logger.debug("Could not found top ads!")

            try:
                bottom_ads_containers = self._driver.find_elements(*self.BOTTOM_ADS_CONTAINER)
                for ad_container in bottom_ads_containers:
                    ads.extend(ad_container.find_elements(*self.AD_RESULTS))

            except NoSuchElementException:
                logger.debug("Could not found bottom ads!")

            self._driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            sleep(1)

        if not ads:
            return []

        # clean non-ad links and duplicates
        ads = set([ad_link for ad_link in ads if ad_link.get_attribute("data-pcu")])

        # if there are filter words given, filter results accordingly
        filtered_ads = []

        if self._filter_words:

            for ad in ads:
                ad_title = ad.find_element(*self.AD_TITLE).text.lower()

                for word in self._filter_words:
                    if word in ad.get_attribute("data-pcu") or word in ad_title:
                        filtered_ads.append(ad)
        else:
            filtered_ads = ads

        ad_links = []

        for ad in filtered_ads:
            logger.info("======= Found an Ad =======")

            ad_link = ad.get_attribute("href")
            ad_title = ad.find_element(*self.AD_TITLE).text
            logger.debug(f"Ad title: {ad_title}, Ad link: {ad_link}")

            ad_links.append((ad, ad_link, ad_title))

        return ad_links

    def _close_cookie_dialog(self) -> None:
        """If cookie dialog is opened, close it by accepting"""

        try:
            cookie_dialog = self._driver.find_element(*self.COOKIE_DIALOG)
            accept_button = cookie_dialog.find_elements(*self.COOKIE_ACCEPT_BUTTON)[-2]
            accept_button.click()
            sleep(1)

        except (NoSuchElementException, ElementNotInteractableException, IndexError):
            pass

    def _is_scroll_at_the_end(self) -> bool:
        """Check if scroll is at the end

        :rtype: bool
        :returns: Whether the scrollbar was reached to end or not
        """

        page_height = self._driver.execute_script("return document.body.scrollHeight;")
        total_scrolled_height = self._driver.execute_script(
            "return window.pageYOffset + window.innerHeight;"
        )

        return page_height - 1 <= total_scrolled_height

    @staticmethod
    def _process_query(query: str) -> tuple[str, list[str]]:
        """Extract search query and filter words from the query input

        Query and filter words are splitted with "@" character. Multiple
        filter words can be used by separating with "#" character.

        e.g. wireless keyboard@amazon#ebay
             bluetooth headphones @ sony # amazon  #bose

        :type query: str
        :param query: Query string with optional filter words
        :rtype tuple
        :returns: Search query and list of filter words if any
        """

        search_query = query.split("@")[0].strip()

        filter_words = []

        if "@" in query:
            filter_words = [word.strip().lower() for word in query.split("@")[1].split("#")]

        return (search_query, filter_words)
