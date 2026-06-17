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


@app.get("/api/clover/test")
def test_clover_connection():
    url = f"{CLOVER_BASE_URL}/v3/merchants/{CLOVER_MERCHANT_ID}"

    response = requests.get(url, headers={
        "Authorization": f"Bearer {CLOVER_ACCESS_TOKEN}"
    })

    return {
        "status_code": response.status_code,
        "response": response.json()
    }

@app.get("/api/clover/create-order")
def test_create_order():
    return create_order()

@app.post("/api/payments")
def create_payment(payment: PaymentRequest):

    cent_conv = int(payment.amount * 100)       # converting amount to int and cents

    #triggering order
    order = create_order()
    order_id = order["id"]

    line_item = add_line_item(
        order_id = order_id,
        description = payment.description,
        amount_cents = cent_conv,
    )

    #recording transaction
    transaction = {
        "timestamp": datetime.utcnow().isoformat(),   
        "order_id": order_id,
        "amt_conv_format": cent_conv,
        "description": payment.description,
        "status": "ORDER_CREATED"  
    }

    with open("apt/transaction.log","a") as file:   #logging transaxtion
        file.write(json.dumps(transaction) + "\n")

    # return result to font page
    return{
        "success": True,
        "status":"SUCCESS",
        "order_id": order_id,
        "line_item": line_item,
        "message": "Payment endpoint working and transaction logged"
    }