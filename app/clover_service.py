import os
import requests
from dotenv import load_dotenv

# for loading env file
load_dotenv()

# loading env variables
CLOVER_BASE_URL= os.getenv("CLOVER_BASE_URL")
CLOVER_MERCHANT_ID= os.getenv("CLOVER_MERCHANT_ID")
CLOVER_ACCESS_TOKEN= os.getenv("CLOVER_ACCESS_TOKEN")
CLOVER_PAYMENT_BASE_URL = os.getenv("CLOVER_PAYMENT_BASE_URL")
CLOVER_PAYMENT_SOURCE_TOKEN = os.getenv("CLOVER_PAYMENT_SOURCE_TOKEN")
CLOVER_TOKEN_BASE_URL = os.getenv("CLOVER_TOKEN_BASE_URL")
CLOVER_ECOMM_PUBLIC_TOKEN = os.getenv("CLOVER_ECOMM_PUBLIC_TOKEN")
CLOVER_ECOMM_PRIVATE_TOKEN = os.getenv("CLOVER_ECOMM_PRIVATE_TOKEN")

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
    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}/orders/{order_id}/line_items"

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

# payment source 
def pay_order(order_id: str, amount_cents: int):
    url = f"{CLOVER_PAYMENT_BASE_URL}/v1/orders/{order_id}/pay"

    payload = {
        "source": CLOVER_PAYMENT_SOURCE_TOKEN,
        "amount": amount_cents,
        "currency": "usd"
    }

    headers = {
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
        "X-Clover-Merchant-Id": CLOVER_MERCHANT_ID,
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload)

    response.raise_for_status()
    return response.json()