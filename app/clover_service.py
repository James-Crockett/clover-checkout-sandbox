import os

import requests
from dotenv import load_dotenv

# for loading env file
load_dotenv()

# loading env variables
CLOVER_BASE_URL = os.getenv("CLOVER_BASE_URL")
CLOVER_TOKEN_BASE_URL = os.getenv("CLOVER_TOKEN_BASE_URL")
CLOVER_MERCHANT_ID = os.getenv("CLOVER_MERCHANT_ID")
CLOVER_ACCESS_TOKEN = os.getenv("CLOVER_ACCESS_TOKEN")
CLOVER_ECOMM_PUBLIC_TOKEN = os.getenv("CLOVER_ECOMM_PUBLIC_TOKEN")
CLOVER_ECOMM_PRIVATE_TOKEN = os.getenv("CLOVER_ECOMM_PRIVATE_TOKEN")


# auth call and data format
def get_headers():
    return {
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


# creating order id
def create_order():
    # merchant order dir
    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}/orders"

    # post, in url location, auth call, empty body for blank order
    response = requests.post(url, headers=get_headers(), json={}, timeout=10)

    # raise exception if any error
    response.raise_for_status()
    return response.json()


# adding items
def add_line_item(order_id: str, description: str, amount_cents: int):
    # order id dir
    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}/orders/{order_id}/line_items"

    # item
    payload = {"name": description, "price": amount_cents}

    # post, in url location, auth call, order info
    response = requests.post(url, headers=get_headers(), json=payload, timeout=10)

    # raise exception if any error
    response.raise_for_status()
    return response.json()


# payment source
def pay_order(order_id: str, source_token: str):
    url = f"https://scl-sandbox.dev.clover.com/v1/orders/{order_id}/pay"

    payload = {"source": source_token}

    headers = {
        "Authorization": f"Bearer {CLOVER_ECOMM_PRIVATE_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    return {"status_code": response.status_code, "body": response.text}


def create_card_token():
    url = f"{CLOVER_TOKEN_BASE_URL}/v1/tokens"

    # sample payload, real info would come from the card readers
    payload = {
        "card": {
            # this test card will fail if there is a lot of transactions
            # "number": "4111111111111111",
            "number": "4242424242424242",
            "exp_month": "12",
            "exp_year": "2035",
            "cvv": "123",
            "last4": "4242",
            "first6": "424242",
            "brand": "VISA",
        }
    }

    headers = {
        "apikey": CLOVER_ECOMM_PUBLIC_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()
