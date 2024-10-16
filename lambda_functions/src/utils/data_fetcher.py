from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from tempfile import mkdtemp
import logging

from .stats_process import PlayerStatsProcessor

class FangraphsScraper:
    @staticmethod
    def initialise_driver():
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")  # Use new headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        chrome_options.add_argument(f"--data-path={mkdtemp()}")
        chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        chrome_options.add_argument("--remote-debugging-pipe")
        chrome_options.add_argument("--window-size=1920,1080")  # Set proper window size
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--log-path=/tmp/chrome.log")
        chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

        service = ChromeService(
            executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
        )

        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

        return driver

    @staticmethod
    def fetch_data(url):
        """
        Fetches data from the specified URL.

        Args:
            url (str): The URL to fetch data from.

        Returns:
            str: The text content of the response.
        """
        driver = FangraphsScraper.initialise_driver()
        driver.get(url)
         # Wait for the page to load
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".fg-data-grid.table-type tbody tr"))
            )
        except TimeoutException as e:
            logging.error("TimeoutException: Element not found within the specified time.")
            logging.error(driver.page_source)  # Print the page source for debugging
            driver.quit()
            raise e
        except Exception as e:
            logging.error("An error occurred while fetching data.")
            logging.error(str(e))
            driver.quit()
            raise e

        html_content = driver.page_source
        driver.quit()
        return html_content
        
    @staticmethod
    def parse_data(html_content, type):
        """
        Parses the data from the Fangraphs website.

        Args:
            data (str): The text content of the response.

        Returns:
            dict: The parsed data.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        # Find the table div by its class
        table_div = soup.find('div', {'class': 'fg-data-grid table-type'})
        rows = table_div.find('table').find_all('tr', class_=True)
        data = {}
        for row in rows:
            columns = row.find_all('td')
            # Get FB data
            if type == "fb":
                name = columns[1].text.strip()
                team = columns[2].text.strip()
                ld = columns[16].text.strip()
                fb = columns[18].text.strip()
                if team not in PlayerStatsProcessor.team_names:
                    continue
                if team not in data:
                    data[team] = {}
                data[team][name] = {
                    'LD': ld,
                    'FB': fb
                }
            # Get Barrel and HardHit data
            elif type == "barrel_hh":
                name = columns[1].text.strip()
                team = columns[2].text.strip()
                event = columns[5].text.strip()
                barrels = columns[9].text.strip()
                hard_hit = columns[11].text.strip()
                if team not in PlayerStatsProcessor.team_names:
                    continue
                if team not in data:
                    data[team] = {}
                data[team][name] = {
                    'Event': event,
                    'Barrels': barrels,
                    'HardHit': hard_hit
                }

        return data

    @staticmethod
    def get_data(url, type, file_path):
        """
        Get the data from a JSON file if it exists and is not outdated,
        otherwise fetch it from the URLs and save it to the file.

        Args:
            urls (list): List of URLs to fetch data from.
            file_path (str): The path to the data JSON file.

        Returns:
            dict: The data.
        """
        # Fetch the data
        html_content = FangraphsScraper.fetch_data(url)
        if html_content:
            parsed_data = FangraphsScraper.parse_data(html_content, type)
        
        return parsed_data
    
    @staticmethod
    def get_past_fifteen_days_dates():
        """
        Get the dates for the past six days in ISO format.

        Returns:
            tuple: Start date and end date in ISO format.
        """
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=14)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

    @staticmethod
    def generate_url(base_url, type):
        """
        Generate the URL with the date range for the past six days.

        Args:
            base_url (str): The base URL to append the date range to.
            type (str): The type of data to fetch ("fb" or "barrel_hh").

        Returns:
            str: The generated URL.
        """
        start_date, end_date = FangraphsScraper.get_past_fifteen_days_dates()
        print(start_date, end_date)
        if type == "fb":
            print(f"{base_url}?season=2024&season1=2024&ind=0&team=0&pageitems=2000000000&sortcol=1&sortdir=asc&type=23&month=1000&startdate={start_date}&enddate={end_date}")
            return f"{base_url}?season=2024&season1=2024&ind=0&team=0&pageitems=2000000000&sortcol=1&sortdir=asc&type=23&month=1000&startdate={start_date}&enddate={end_date}"
        elif type == "barrel_hh":
            return f"{base_url}?season=2024&season1=2024&ind=0&team=0&pageitems=2000000000&sortcol=1&sortdir=asc&type=24&month=1000&startdate={start_date}&enddate={end_date}"
