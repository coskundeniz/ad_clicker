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
    RESULTS_CONTAINER = (By.ID, "result-stats")
    COOKIE_DIALOG = (By.CSS_SELECTOR, "div[role='dialog']")
    COOKIE_ACCEPT_BUTTON = (By.TAG_NAME, "button")
    TOP_ADS_CONTAINER = (By.ID, "tads")
    BOTTOM_ADS_CONTAINER = (By.ID, "tadsb")
    AD_RESULTS = (By.CSS_SELECTOR, "div > a")
    AD_TITLE = (By.CSS_SELECTOR, "div[role='heading']")

    def __init__(self, driver: selenium.webdriver, query: str, ad_visit_time: int) -> None:

        self._driver = driver
        self._search_query = query
        self._ad_visit_time = ad_visit_time

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
        empty_ads_container = 0

        try:
            ads_container = self._driver.find_element(*self.TOP_ADS_CONTAINER)
            ads = ads_container.find_elements(*self.AD_RESULTS)

        except NoSuchElementException:
            logger.debug("Could not found top ads!")
            empty_ads_container += 1

        try:
            bottom_ads_container = self._driver.find_element(*self.BOTTOM_ADS_CONTAINER)
            ads.extend(bottom_ads_container.find_elements(*self.AD_RESULTS))

        except NoSuchElementException:
            logger.debug("Could not found bottom ads!")
            empty_ads_container += 1

        if empty_ads_container == 2:
            return []

        # clean sublinks
        ads = [ad_link for ad_link in ads if ad_link.get_attribute("data-pcu")]

        ad_links = []

        for ad in ads:
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
