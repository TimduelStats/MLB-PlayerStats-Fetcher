from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import pytz
import os
from .stats_process import PlayerStatsProcessor
# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


class FangraphsScraper:
    @staticmethod
    def fetch_data(url):
        """
        Fetches data from the specified URL.

        Args:
            url (str): The URL to fetch data from.

        Returns:
            str: The text content of the response.
        """
        # Use Selenium to fetch the data
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        driver_path = ChromeDriverManager().install()
        if driver_path:
            driver_name = driver_path.split('/')[-1]
            if driver_name!="chromedriver":
                driver_path = "/".join(driver_path.split('/')[:-1]+["chromedriver"])
                os.chmod(driver_path, 0o755)
        driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)

        driver.get(url)
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".fg-data-grid.table-type tbody tr"))
        )

        html_content = driver.page_source
        driver.quit()
        return html_content

    @staticmethod
    def load_data(file_path="../../../../data/fangraphs_data.json"):
        """
        Loads the data from a JSON file.

        Args:
            file_path (str): The path to the JSON file.

        Returns:
            dict: The loaded data.
        """
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return None
        
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
    def save_data(data, file_path="../../../../data/fangraphs_data.json"):
        """
        Saves the data to a JSON file.

        Args:
            data (dict): The data to save.
            file_path (str): The path to the JSON file.
        """
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
    @staticmethod
    def get_or_fetch_data(url, type, file_path):
        """
        Get the data from a JSON file if it exists and is not outdated,
        otherwise fetch it from the URLs and save it to the file.

        Args:
            urls (list): List of URLs to fetch data from.
            file_path (str): The path to the data JSON file.

        Returns:
            dict: The data.
        """
        est = pytz.timezone('US/Eastern')
        now_est = datetime.now(est)

        # Check if the file exists and is not outdated
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path), tz=est)
            file_date = file_mtime.date()
            today_date = now_est.date()

            if file_date == today_date:
                return FangraphsScraper.load_data(file_path)
        
        # Fetch the data
        html_content = FangraphsScraper.fetch_data(url)
        if html_content:
            parsed_data = FangraphsScraper.parse_data(html_content, type)
        FangraphsScraper.save_data(parsed_data, file_path)
        
        return parsed_data
    
    @staticmethod
    def get_past_six_days_dates():
        """
        Get the dates for the past six days in ISO format.

        Returns:
            tuple: Start date and end date in ISO format.
        """
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=5)
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
        start_date, end_date = FangraphsScraper.get_past_six_days_dates()
        print(start_date, end_date)
        if type == "fb":
            print(f"{base_url}?pos=all&stats=bat&lg=all&season=2024&season1=2024&ind=0&team=0&pageitems=2000000000&qual=5&sortcol=1&sortdir=asc&type=23&month=1000&startdate={start_date}&enddate={end_date}")
            return f"{base_url}?pos=all&stats=bat&lg=all&season=2024&season1=2024&ind=0&team=0&pageitems=2000000000&qual=5&sortcol=1&sortdir=asc&type=23&month=1000&startdate={start_date}&enddate={end_date}"
        elif type == "barrel_hh":
            return f"{base_url}?pos=all&stats=bat&lg=all&season=2024&season1=2024&ind=0&team=0&pageitems=2000000000&qual=5&sortcol=1&sortdir=asc&type=24&month=1000&startdate={start_date}&enddate={end_date}"
