import json
import os
import sys

# Add the parent directory to the system path to find utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
print(parent_dir)
sys.path.append(parent_dir)

from datetime import datetime, timedelta
import pytz
from utils.data_fetcher import FangraphsScraper
# from utils.s3_uploader import upload_to_s3



def lambda_handler(event, context):
    base_url_fb = "https://www.fangraphs.com/leaders/major-league"
    url_fb = FangraphsScraper.generate_url(base_url_fb, "fb")
    data_fb = FangraphsScraper.get_or_fetch_data(url_fb, "fb", file_path="/tmp/fangraphs_fb_data.json")

    base_url_barrel_hh = "https://www.fangraphs.com/leaders/major-league"
    url_barrel_hh = FangraphsScraper.generate_url(base_url_barrel_hh, "barrel_hh")
    data_barrel_hh = FangraphsScraper.get_or_fetch_data(url_barrel_hh, "barrel_hh", file_path="/tmp/fangraphs_barrel_hh_data.json")

    # upload_to_s3('/tmp/fangraphs_fb_data.json', 'your-bucket-name', 'fangraphs_fb_data.json')
    # upload_to_s3('/tmp/fangraphs_barrel_hh_data.json', 'your-bucket-name', 'fangraphs_barrel_hh_data.json')

    # Write to local for testing
    with open('./fangraphs_fb_data.json', 'w') as f:
        json.dump(data_fb, f, indent=4, ensure_ascii=False)
    with open('./fangraphs_barrel_hh_data.json', 'w') as f:
        json.dump(data_barrel_hh, f, indent=4, ensure_ascii=False)
    return {
        'statusCode': 200,
        'body': json.dumps('Data fetched and saved successfully')
    }

if __name__ == "__main__":
    # Mock event and context for local testing
    event = {}
    context = {}
    response = lambda_handler(event, context)
    print(response)