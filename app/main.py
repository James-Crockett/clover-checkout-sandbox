import os
import requests

import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from pydantic import BaseModel, Field
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.clover_service import create_order, add_line_item
from app.clover_service import create_order
from app.clover_service import create_card_token
from app.clover_service import pay_order

app = FastAPI()
load_dotenv()

CLOVER_OAUTH_BASE_URL = os.getenv("CLOVER_OAUTH_BASE_URL")
CLOVER_APP_ID = os.getenv("CLOVER_APP_ID")
CLOVER_APP_SECRET = os.getenv("CLOVER_APP_SECRET")
CLOVER_REDIRECT_URI = os.getenv("CLOVER_REDIRECT_URI")
CLOVER_BASE_URL = os.getenv("CLOVER_BASE_URL")
CLOVER_MERCHANT_ID = os.getenv("CLOVER_MERCHANT_ID")
CLOVER_ACCESS_TOKEN = os.getenv("CLOVER_ACCESS_TOKEN")

# CORS preflight request handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# defining datamodel for request
# using pydantic to handle validation
class PaymentRequest(BaseModel):
    amount: float = Field(gt = 0)                 # amount should always be +ve and greater than 0.
    description: str = Field(min_length = 1)      # cannot be an empty string

def process_test_payment(order_id: str, amount_cents: int):
    return {
        "id": None,
        "status": "PAYMENT_NOT_IMPLEMENTED",
        "message": "Order and line item created. Payment token integration pending.",
        "order_id": order_id,
        "amount_cents": amount_cents,
    }

@app.get("/")
def root():
    return {
        "message": "Payment backend running"
    }

# adding oauth routes
@app.get("/oauth/start")
def oauth_start():
    auth_url = (
        f"{CLOVER_OAUTH_BASE_URL}/oauth/authorize"
        f"?client_id={CLOVER_APP_ID}"
        f"&redirect_uri={CLOVER_REDIRECT_URI}"
        f"&response_type=code"
    )

    return RedirectResponse(auth_url)

# adding oauth callback
@app.get("/oauth/callback")
def oauth_callback(code: str, merchant_id: str | None = None):
    token_url = f"{CLOVER_OAUTH_BASE_URL}/oauth/token"

    payload = {
        "client_id": CLOVER_APP_ID,
        "client_secret": CLOVER_APP_SECRET,
        "code": code,
        "redirect_uri": CLOVER_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=payload)

    return {
        "status_code": response.status_code,
        "response": response.json(),
        "merchant_id": merchant_id,
    }

@app.post("/api/payments")
def create_payment(payment: PaymentRequest):

    cent_conv = int(payment.amount * 100)       # converting amount to int and cents

    # Create an order
    # Add the requested item as a line item
    # Generate a sandbox card token
    # Submit payment for the order
    # Parse the payment response for logging and API output
    order = create_order()
    line_item = add_line_item(order["id"], payment.description, amount_cents)
    card_token = create_card_token()
    payment_result = pay_order(order["id"], card_token["id"])
    payment_body = json.loads(payment_result["body"])

    line_item = add_line_item(
        order_id = order_id,
        description = payment.description,
        amount_cents = cent_conv
    )

    payment_result = pay_order(order_id, amount_cents)

    #recording transaction
    transaction = {
        "timestamp": datetime.utcnow().isoformat(),
        "order_id": order["id"],
        "line_item_id": line_item.get("id"),
        "amount": payment.amount,
        "amount_cents": amount_cents,
        "description": payment.description,
        "status": payment_result["body"]
    }

    with open("apt/transaction.log","a") as file:   #logging transaxtion
        file.write(json.dumps(transaction) + "\n")


    
    # return result to font page
    return {
        "success": True,
        "status": payment_body.get("status"),
        "order_id": order["id"],
        "amount_paid": payment_body.get("amount_paid"),
        "charge_id": payment_body.get("charge"),
        "payment": payment_body
    }
