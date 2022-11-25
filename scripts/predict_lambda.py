import requests
from loguru import logger

API_KEY = 'YOUR_API_KEY'
API_URL = 'https://njs0kuvzkj.execute-api.us-west-1.amazonaws.com/prod/predict-price'

sample_data = {'brand_name': 'lenovo',
               'proc_freq': 1.2,
               'proc_brand': 'amd',
               'proc_name': 'amd',
               'proc_count': 2.0,
               'videocard': 'radeon',
               'videocard_memory': 8.0,
               'screen': 11.0,
               'ssd_volume': 0,
               'ram': 4,
               'hdmi': True,
               'material': 'пластик',
               'battery_life': 8.0}


def main():
    logger.info("Start predicting")
    logger.info(f"Sample data: {sample_data}")
    logger.info(f"Running API call ... {API_URL}")
    response = requests.post(API_URL, json=sample_data, headers={'x-api-key': API_KEY})
    logger.info(f"API response: {response.json()}")
    logger.info(f"Finished predicting")


if __name__ == "__main__":
    main()
