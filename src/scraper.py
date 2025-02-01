from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List
from datetime import datetime
import json
import os

class NestedModel1(BaseModel):
    address: str = Field(alias='location')  # Map location to address
    number_of_units: float = Field(default=0)  # Default to 0
    square_footage: str = Field(default='N/A')  # Default to N/A
    url: str = Field(default=None)
    contact_info: str = Field(default='N/A')  # Default to N/A
    price: str = Field(default='N/A')  # Default to N/A

class ExtractSchema(BaseModel):
    listings: List[NestedModel1]

import logging

def scrape_real_estate(api_key):
    logging.info('Starting real estate scraping process')
    app = FirecrawlApp(api_key=api_key)
    
    # Prepare the request payload
    payload = {
        'prompt': 'Ensure that the address is always included for each commercial real estate listing. Extract the number of units available, square footage, URL of the listing, contact information, and price.',
        'schema': ExtractSchema.model_json_schema(),
        'urls': [
            "https://loopnet.com/search/commercial-real-estate/new-york-ny/for-lease/*",
            "https://www.showcase.com/ny/new-york/commercial-real-estate/for-rent/*"
        ]
    }
    
    # Log the schema
    schema = ExtractSchema.model_json_schema()
    logging.info(f'Using schema: {json.dumps(schema, indent=2)}')
    
    # Make the API request
    logging.info('Sending extraction request to Firecrawl API')
    try:
        try:
            data = app.extract(
                [
                    "https://www.loopnet.com/search/commercial-real-estate/new-york-ny/for-lease/"
                ],
                {
                    'prompt': 'Extract all commercial real estate listings. For each listing, get the address, number of units available, square footage, URL, contact information, and price.',
                    'schema': ExtractSchema.model_json_schema()
                }
            )
        except Exception as api_error:
            logging.error(f'Error during Firecrawl API call: {str(api_error)}')
            logging.error(f'API error type: {type(api_error)}')
            raise
        logging.info('Successfully received response from Firecrawl API')
        logging.info(f'Raw response data: {data}')
        
        # Check the structure of the response
        if isinstance(data, dict):
            logging.info(f'Response keys: {list(data.keys())}')
            if 'data' in data:
                logging.info(f'Data keys: {list(data["data"].keys())}')
                if 'listings' in data['data']:
                    listings = data['data']['listings']
                    logging.info(f'Found {len(listings)} listings')
                    if listings:
                        logging.info(f'Sample listing: {listings[0]}')
                else:
                    logging.warning('No "listings" key in data')
            else:
                logging.warning('No "data" key in response')
        else:
            logging.warning(f'Unexpected response type: {type(data)}')
    except Exception as e:
        logging.error(f'Error during API request: {str(e)}')
        raise
    
    # Save raw data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'data/raw_data_{timestamp}.json'
    logging.info(f'Saving data to {filename}')
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info('Data saved successfully')
    except Exception as e:
        logging.error(f'Error saving data: {str(e)}')
        raise
    
    return data

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    scrape_real_estate()
