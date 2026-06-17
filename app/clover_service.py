import os
import requests
from dotenv import load_dotenv

# for loading env file
load_dotenv()

# loading env variables
CLOVER_BASE_URL= os.getenv("CLOVER_BASE_URL")
CLOVER_MERCHANT_ID= os.getenv("CLOVER_MERCHANT_ID")
CLOVER_ACCESS_TOKEN= os.getenv("CLOVER_ACCESS_TOLKEN")

# auth call and data format
def get_headers():
    return{
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

# creating order id
def create_order():
    # merchant order dir
    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}/orders"

    # post, in url location, auth call, empty body for blank order
    response = requests.post(
        url,
        headers = get_headers(),
        json = {}
    )

    # raise exception if any error
    response.raise_for_status()
    return response.json()

# adding items
def add_line_item (order_id: str, description: str, amount_cents: int):
    #order id dir
    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}/orders{order_id}/line_items"

    # item
    payload= {
        "name": description,
        "price": amount_cents
    }

    # post, in url location, auth call, order info
    response = requests.post(
        url,
        headers = get_headers(),
        json = payload
    )
    # raise exception if any error
    response.raise_for_status()
    return response.json()