import json
import os
import sys

# Add the parent directory to the system path to find utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.data_fetcher import FangraphsScraper
from utils.s3_uploader import upload_to_s3

BUCKET_NAME = 'timjimmymlbdata'

def lambda_handler(event, context):
    base_url_fb = "https://www.fangraphs.com/leaders/major-league"
    url_fb = FangraphsScraper.generate_url(base_url_fb, "fb")
    data_fb = FangraphsScraper.get_data(url_fb, "fb", file_path="/tmp/fangraphs_fb_data.json")

    base_url_barrel_hh = "https://www.fangraphs.com/leaders/major-league"
    url_barrel_hh = FangraphsScraper.generate_url(base_url_barrel_hh, "barrel_hh")
    data_barrel_hh = FangraphsScraper.get_data(url_barrel_hh, "barrel_hh", file_path="/tmp/fangraphs_barrel_hh_data.json")

    # Write to /tmp directory for Lambda environment
    fb_data_path = '/tmp/fangraphs_fb_data.json'
    barrel_hh_data_path = '/tmp/fangraphs_barrel_hh_data.json'

    # Write to tmp
    with open(fb_data_path, 'w') as f:
        json.dump(data_fb, f, indent=4, ensure_ascii=False)
    with open(barrel_hh_data_path, 'w') as f:
        json.dump(data_barrel_hh, f, indent=4, ensure_ascii=False)

    upload_to_s3(fb_data_path, BUCKET_NAME, 'fangraphs_fb_data.json')
    upload_to_s3(barrel_hh_data_path, BUCKET_NAME, 'fangraphs_barrel_hh_data.json')

    return {
        'statusCode': 200,
        'body': json.dumps('Data fetched and saved successfully')
    }

