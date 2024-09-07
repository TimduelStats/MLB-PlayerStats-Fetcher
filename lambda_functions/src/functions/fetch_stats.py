import json
import os
import sys

# Add the parent directory to the system path to find utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.data_fetcher import FangraphsScraper
from utils.today_statcast_hh_data_fetcher import FangraphsStatcastScraper
from utils.today_stats_fb_data_fetcher import FangraphsStatsScraper
from utils.s3_uploader import upload_to_s3
from utils.s3_uploader import delete_from_s3

from datetime import datetime, timedelta

BUCKET_NAME = 'timjimmymlbdata'

def lambda_handler(event, context):
    # Delete existing files from S3 first
    delete_from_s3(BUCKET_NAME, 'fangraphs_fb_data.json');
    delete_from_s3(BUCKET_NAME, 'fangraphs_barrel_hh_data.json');

    # Get today's date and get today's hh and fb data
    today = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=15)).strftime('%Y-%m-%d')
    # Save csv to /tmp as well
    FangraphsStatsScraper.get_batter_fb_for_date(start_date, file_path="/tmp/today_fb_data.csv")
    FangraphsStatcastScraper.get_batter_hh_for_date(start_date, file_path="/tmp/today_hh_data.csv")

    # This is for mlb main page data
    base_url_fb = "https://www.fangraphs.com/leaders/major-league"
    url_fb = FangraphsScraper.generate_url(base_url_fb, "fb")
    data_fb = FangraphsScraper.get_data(url_fb, "fb", file_path="/tmp/fangraphs_fb_data.json")
    print("getting data for barrel_hh")
    base_url_barrel_hh = "https://www.fangraphs.com/leaders/major-league"
    url_barrel_hh = FangraphsScraper.generate_url(base_url_barrel_hh, "barrel_hh")
    data_barrel_hh = FangraphsScraper.get_data(url_barrel_hh, "barrel_hh", file_path="/tmp/fangraphs_barrel_hh_data.json")
    print("get data for barrel_hh")
    # Write to /tmp directory for Lambda environment 
    fb_data_path = '/tmp/fangraphs_fb_data.json'
    barrel_hh_data_path = '/tmp/fangraphs_barrel_hh_data.json'
    today_fb_data_path = '/tmp/today_fb_data.csv'
    today_hh_data_path = '/tmp/today_hh_data.csv'

    # Write to tmp, because data_fb and data_barrel_hh are dictionaries
    with open(fb_data_path, 'w') as f:
        json.dump(data_fb, f, indent=4, ensure_ascii=False)
    with open(barrel_hh_data_path, 'w') as f:
        json.dump(data_barrel_hh, f, indent=4, ensure_ascii=False)


    # Upload to S3
    upload_to_s3(fb_data_path, BUCKET_NAME, 'fangraphs_fb_data.json')
    upload_to_s3(barrel_hh_data_path, BUCKET_NAME, 'fangraphs_barrel_hh_data.json')
    upload_to_s3(today_fb_data_path, BUCKET_NAME, 'today_fb_data.csv')
    upload_to_s3(today_hh_data_path, BUCKET_NAME, 'today_hh_data.csv')

    return {
        'statusCode': 200,
        'body': json.dumps('Data fetched and saved successfully')
    }

