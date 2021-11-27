from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
from webdriver_setup import get_webdriver_for

from config import logger


class SearchController:

    URL = "https://www.google.com"
    SEARCH_INPUT = (By.NAME, "q")

    def __init__(self, query, browser="firefox"):

        self._search_query = query

        self._driver = self._create_driver(browser)
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
            results_loaded = wait.until(EC.presence_of_element_located((By.ID, "result-stats")))

            if results_loaded:
                logger.info("Getting ad links...")
                ad_links = self._get_ad_links()

        except TimeoutException:
            logger.error("Timed out waiting for results!")
            self.end_search()

        return ad_links

    def click_ads(self, ads):
        """Click ads found

        :type ads: list
        :param ads: List of (ad, ad_link) tuples
        """

        # store the ID of the original window
        original_window_handle = self._driver.current_window_handle

        for ad in ads:
            ad_link_element = ad[0]
            ad_link = ad[1]
            logger.info(f"Clicking {ad_link}...")

            # open link in a different tab
            actions = ActionChains(self._driver)
            actions.key_down(Keys.CONTROL)
            actions.click(ad_link_element)
            actions.key_up(Keys.CONTROL)
            actions.perform()

            for window_handle in self._driver.window_handles:
                if window_handle != original_window_handle:
                    self._driver.switch_to.window(window_handle)
                    sleep(4)
                    self._driver.close()
                    break

            # go back to original window
            self._driver.switch_to.window(original_window_handle)
            sleep(1)

            # scroll the page to avoid elements remain outside of the view
            self._driver.execute_script("arguments[0].scrollIntoView(true);", ad_link_element)

    def end_search(self):
        """Close the browser"""

        self._driver.quit()

    def _create_driver(self, browser):

        try:
            driver = get_webdriver_for(browser)
        except ValueError:
            logger.error(f"{browser} is not installed on your system!")
            raise SystemExit()

        return driver

    def _load(self):
        """Load Google main page"""

        self._driver.get(self.URL)

    def _get_ad_links(self):
        """Extract ad links to click

        :rtype: list
        :returns: List of (ad, ad_link) tuples
        """

        ad_links = []

        try:
            ads_container = self._driver.find_element(By.ID, "tads")
        except NoSuchElementException as exp:
            logger.debug(exp)
            return ad_links

        ads = ads_container.find_elements(By.CSS_SELECTOR, "div > a")

        for ad in ads:
            ad_text = ad.text.lower()
            if ("reklam" in ad_text) or ("ad" in ad_text):
                logger.info("======= Found an Ad =======")
                ad_link = ad.get_attribute("href")
                logger.debug(f"Ad Link: {ad_link}")
                ad_links.append((ad, ad_link))

        return ad_links
