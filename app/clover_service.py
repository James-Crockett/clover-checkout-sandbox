import json
import os
import time

import requests
from dotenv import load_dotenv

# for loading env file
load_dotenv()

# loading env variables
CLOVER_BASE_URL = os.getenv("CLOVER_BASE_URL")
CLOVER_TOKEN_BASE_URL = os.getenv("CLOVER_TOKEN_BASE_URL")
CLOVER_APP_ID = os.getenv("CLOVER_APP_ID")
CLOVER_OAUTH_API_URL = os.getenv("CLOVER_OAUTH_API_URL")
CLOVER_ECOMM_PUBLIC_TOKEN = os.getenv("CLOVER_ECOMM_PUBLIC_TOKEN")
CLOVER_ECOMM_PRIVATE_TOKEN = os.getenv("CLOVER_ECOMM_PRIVATE_TOKEN")


def load_oauth_tokens():
    with open("app/oauth_tokens.json") as file:
        return json.load(file)


def access_token_expired(token_data: dict):
    return time.time() >= token_data["access_token_expiration"]


def refresh_oauth_tokens(refresh_token: str):
    # exchange clover single-use refresh token for a new token pair
    url = f"{CLOVER_OAUTH_API_URL}/oauth/v2/refresh"
    payload = {"client_id": CLOVER_APP_ID, "refresh_token": refresh_token}

    # stop if clover rejects or cannot process the refresh request
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()

    # caller will replace the stored access and refresh tokens with this pair
    return response.json()


# auth call and data format
def get_headers():
    token_data = load_oauth_tokens()

    # refresh and store the token pair before using an expired access token
    if access_token_expired(token_data):
        try:
            new_tokens = refresh_oauth_tokens(token_data["refresh_token"])
        except requests.RequestException as error:
            raise RuntimeError(
                "clover authorization expired, visit /oauth/start"
            ) from error

        new_tokens["merchant_id"] = token_data["merchant_id"]
        with open("app/oauth_tokens.json", "w") as file:
            json.dump(new_tokens, file)
        os.chmod("app/oauth_tokens.json", 0o600)
        token_data = new_tokens

    return {
        "Authorization": f"Bearer {token_data['access_token']}",
        "Content-Type": "application/json",
    }


# creating order id
def create_order():
    # merchant order dir
    merchant_id = load_oauth_tokens()["merchant_id"]
    url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant_id}/orders"

    # post, in url location, auth call, empty body for blank order
    response = requests.post(url, headers=get_headers(), json={}, timeout=10)

    # raise exception if any error
    response.raise_for_status()
    return response.json()


# adding items
def add_line_item(order_id: str, description: str, amount_cents: int):
    # order id dir
    merchant_id = load_oauth_tokens()["merchant_id"]
    url = f"{CLOVER_BASE_URL}/v3/merchants/{merchant_id}/orders/{order_id}/line_items"

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
