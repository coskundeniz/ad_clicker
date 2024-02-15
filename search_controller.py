"""
BİR ADAM

Korku dağlarının yürekçisi,
Ölüm denizlerinin kürekçisi;
Öyle suskun oturuyor şişesinin başında,
İçtiğinin hem hırsızı, hem bekçisi,

Onu kırmış olmalı yaşamında birisi.
Dinledikçe susması, düşündükçe susması..
Tek başına iki kişi olmuş kendisiyle
gölgesi,
Heykelini yontuyor yalnızlığın ustası.

                            -- Özdemir Asaf
"""

import sys
import random
from time import sleep

import selenium
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

from config import logger


AdList = list[tuple[selenium.webdriver.remote.webelement.WebElement, str, str]]


class SearchController:
    """Search controller for ad clicker

    :type driver: selenium.webdriver
    :param driver: Selenium Chrome webdriver instance
    :type query: str
    :param query: Search query
    :type max_scroll_limit: int
    :param max_scroll_limit: Number of maximum scrolls on the search results page
    :type excludes: str
    :param excludes: Words to exclude ads containing them in url or title
    """

    URL = "https://www.google.com"

    SEARCH_INPUT = (By.NAME, "q")
    RESULTS_CONTAINER = (By.ID, "appbar")
    COOKIE_DIALOG_BUTTON = (By.TAG_NAME, "button")
    TOP_ADS_CONTAINER = (By.ID, "tads")
    BOTTOM_ADS_CONTAINER = (By.ID, "tadsb")
    AD_RESULTS = (By.CSS_SELECTOR, "div > a")
    AD_TITLE = (By.CSS_SELECTOR, "div[role='heading']")

    def __init__(
        self, driver: selenium.webdriver, query: str, max_scroll_limit: int, excludes: str = None
    ) -> None:
        self._driver = driver
        self._max_scroll_limit = max_scroll_limit
        self._search_query, self._filter_words = self._process_query(query)
        self._exclude_list = None

        if excludes:
            self._exclude_list = [item.strip() for item in excludes.split(",")]
            logger.debug(f"Words to be excluded: {self._exclude_list}")

        self._load()

    def search_for_ads(self) -> AdList:
        """Start search for the given query and return ads if any

        :rtype: list
        :returns: List of (ad, ad_link, ad_title) tuples
        """

        logger.info(f"Starting search for '{self._search_query}'")
        sleep(1)

        self._close_cookie_dialog()

        try:
            search_input_box = self._driver.find_element(*self.SEARCH_INPUT)
            search_input_box.send_keys(self._search_query, Keys.ENTER)
        except ElementNotInteractableException:
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
                ad_links = self._get_ad_links()

        except TimeoutException:
            logger.error("Timed out waiting for results!")
            self.end_search()
            raise SystemExit()

        return ad_links

    def click_ads(self, ads: AdList) -> None:
        """Click ads found

        :type ads: AdList
        :param ads: List of (ad, ad_link, ad_title) tuples
        """

        # scroll to the top of the page
        self._driver.find_element(By.TAG_NAME, "body").send_keys(Keys.HOME)
        sleep(1)

        platform = sys.platform

        control_command_key = Keys.COMMAND if platform.endswith("darwin") else Keys.CONTROL

        # store the ID of the original window
        original_window_handle = self._driver.current_window_handle

        for ad in ads:
            try:
                ad_link_element = ad[0]
                ad_link = ad[1]
                ad_title = ad[2]
                logger.info(f"Clicking to [{ad_title}]({ad_link})...")

                # open link in a different tab
                actions = ActionChains(self._driver)
                actions.move_to_element(ad_link_element)
                actions.key_down(control_command_key)
                actions.click()
                actions.key_up(control_command_key)
                actions.perform()
                sleep(0.5)

                if len(self._driver.window_handles) != 2:
                    logger.debug("Couldn't click! Scrolling element into view...")

                    self._driver.execute_script(
                        "arguments[0].scrollIntoView(true);", ad_link_element
                    )

                    actions = ActionChains(self._driver)
                    actions.move_to_element(ad_link_element)
                    actions.key_down(control_command_key)
                    actions.click()
                    actions.key_up(control_command_key)
                    actions.perform()
                    sleep(0.5)

                else:
                    logger.debug("Opened link in a new tab. Switching to tab...")

                for window_handle in self._driver.window_handles:
                    if window_handle != original_window_handle:
                        self._driver.switch_to.window(window_handle)
                        sleep(random.choice(range(4, 9)))

                        logger.debug(f"Current url on new tab: {self._driver.current_url}")

                        self._driver.close()
                        break

                # go back to original window
                self._driver.switch_to.window(original_window_handle)
                sleep(1)

                # scroll the page to avoid elements remain outside of the view
                self._driver.execute_script("arguments[0].scrollIntoView(true);", ad_link_element)

            except StaleElementReferenceException:
                logger.debug(f"Ad element [{ad_title}] has changed. Skipping scroll into view...")

    def end_search(self) -> None:
        """Close the browser"""

        if self._driver:
            logger.info("Closing the browser...")

            try:
                self._driver.delete_all_cookies()
                self._driver.quit()

            except OSError as exp:
                logger.debug(exp)

            self._driver = None

    def _load(self) -> None:
        """Load Google main page"""

        self._driver.get(self.URL)

    def _get_ad_links(self) -> AdList:
        """Extract ad links to click

        :rtype: AdList
        :returns: List of (ad, ad_link, ad_title) tuples
        """

        logger.info("Getting ad links...")

        ads = []

        scroll_count = 0

        logger.debug(f"Max scroll limit: {self._max_scroll_limit}")

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

            if self._max_scroll_limit > 0 and scroll_count == self._max_scroll_limit:
                logger.debug("Reached to max scroll limit! Ending scroll...")
                break

            self._driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            sleep(2)

            scroll_count += 1

        if not ads:
            return []

        # clean non-ad links and duplicates
        cleaned_ads = []
        links = []

        for ad in ads:
            if ad.get_attribute("data-pcu"):
                ad_link = ad.get_attribute("href")

                if ad_link not in links:
                    links.append(ad_link)
                    cleaned_ads.append(ad)

        # if there are filter words given, filter results accordingly
        filtered_ads = []

        if self._filter_words:
            for ad in cleaned_ads:
                ad_title = ad.find_element(*self.AD_TITLE).text.lower()
                ad_link = ad.get_attribute("data-pcu")

                for word in self._filter_words:
                    if word in ad_link or word in ad_title:
                        if ad not in filtered_ads:
                            logger.debug(f"Filtering [{ad_title}]: {ad_link}")
                            filtered_ads.append(ad)
        else:
            filtered_ads = cleaned_ads

        ad_links = []

        for ad in filtered_ads:
            ad_link = ad.get_attribute("href")
            ad_title = ad.find_element(*self.AD_TITLE).text
            logger.debug(f"Ad title: {ad_title}, Ad link: {ad_link}")

            if self._exclude_list:
                for exclude_item in self._exclude_list:
                    if (
                        exclude_item in ad.get_attribute("data-pcu")
                        or exclude_item.lower() in ad_title.lower()
                    ):
                        logger.debug(f"Excluding [{ad_title}]: {ad_link}")
                        break
                else:
                    logger.info("======= Found an Ad =======")
                    ad_links.append((ad, ad_link, ad_title))
            else:
                logger.info("======= Found an Ad =======")
                ad_links.append((ad, ad_link, ad_title))

        return ad_links

    def _close_cookie_dialog(self) -> None:
        """If cookie dialog is opened, close it by accepting"""

        logger.debug("Waiting for cookie dialog...")

        sleep(3)

        all_links = [
            element.get_attribute("href")
            for element in self._driver.find_elements(By.TAG_NAME, "a")
            if isinstance(element.get_attribute("href"), str)
        ]

        for link in all_links:
            if "policies.google.com" in link:
                buttons = self._driver.find_elements(*self.COOKIE_DIALOG_BUTTON)[6:-2]
                if len(buttons) < 6:
                    buttons = self._driver.find_elements(*self.COOKIE_DIALOG_BUTTON)

                for button in buttons:
                    try:
                        if button.get_attribute("role") != "link":
                            logger.debug(f"Clicking button {button.get_attribute('outerHTML')}")
                            self._driver.execute_script(
                                "arguments[0].scrollIntoView(true);", button
                            )
                            sleep(1)
                            button.click()
                            sleep(1)

                            try:
                                search_input_box = self._driver.find_element(*self.SEARCH_INPUT)
                                search_input_box.send_keys(self._search_query)
                                search_input_box.clear()
                                break
                            except (
                                ElementNotInteractableException,
                                StaleElementReferenceException,
                            ):
                                pass

                    except (
                        ElementNotInteractableException,
                        ElementClickInterceptedException,
                        StaleElementReferenceException,
                    ):
                        pass

                sleep(1)
                break
        else:
            logger.debug("No cookie dialog found! Continue with search...")

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
