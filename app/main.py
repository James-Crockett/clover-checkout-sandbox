import json
import os
from datetime import UTC, datetime
from decimal import Decimal

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException

from app.clover_service import add_line_item, create_card_token, create_order, pay_order

app = FastAPI()
load_dotenv()

CLOVER_APP_ID = os.getenv("CLOVER_APP_ID")
CLOVER_APP_SECRET = os.getenv("CLOVER_APP_SECRET")
CLOVER_REDIRECT_URI = os.getenv("CLOVER_REDIRECT_URI")
CLOVER_OAUTH_AUTHORIZE_URL = os.getenv("CLOVER_OAUTH_AUTHORIZE_URL")
CLOVER_OAUTH_API_URL = os.getenv("CLOVER_OAUTH_API_URL")


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
    amount: Decimal = Field(gt=0)  # amount should always be +ve and greater than 0.
    description: str = Field(min_length=1)  # cannot be an empty string


@app.get("/")
def root():
    return {"message": "Payment backend running"}


# adding oauth routes
@app.get("/oauth/start")
def oauth_start():
    auth_url = (
        f"{CLOVER_OAUTH_AUTHORIZE_URL}/oauth/v2/authorize"
        f"?client_id={CLOVER_APP_ID}"
        f"&redirect_uri={CLOVER_REDIRECT_URI}"
        f"&response_type=code"
    )

    return RedirectResponse(auth_url)


# adding oauth callback
@app.get("/oauth/callback")
def oauth_callback(code: str, merchant_id: str | None = None):
    token_url = f"{CLOVER_OAUTH_API_URL}/oauth/v2/token"

    payload = {
        "client_id": CLOVER_APP_ID,
        "client_secret": CLOVER_APP_SECRET,
        "code": code,
        "redirect_uri": CLOVER_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, json=payload, timeout=10)
    response.raise_for_status()
    token_data = response.json()

    return {
        "status_code": response.status_code,
        "response": token_data,
        "merchant_id": merchant_id,
    }


@app.post("/api/payments")
def create_payment(payment: PaymentRequest):
    try:
        amount_cents = int(payment.amount * 100)  # converting amount to int and cents

        # create an order
        # add the requested item as a line item
        # generate a sandbox card token
        # submit payment for the order
        # parse the payment response for logging and API output
        order = create_order()
        line_item = add_line_item(order["id"], payment.description, amount_cents)
        card_token = create_card_token()
        payment_result = pay_order(order["id"], card_token["id"])
        payment_body = json.loads(payment_result["body"])

        # recording transaction
        transaction = {
            "timestamp": datetime.now(UTC).isoformat(),
            "order_id": order["id"],
            "line_item_id": line_item.get("id"),
            "amount": float(payment.amount),
            "amount_cents": amount_cents,
            "description": payment.description,
            "status": payment_body.get("status"),
            "charge_id": payment_body.get("charge"),
        }

        with open("app/transaction.log", "a") as file:  # logging transaxtion
            file.write(json.dumps(transaction) + "\n")

        # return result to font page
        return {
            "success": True,
            "status": payment_body.get("status"),
            "order_id": order["id"],
            "amount_paid": payment_body.get("amount_paid"),
            "charge_id": payment_body.get("charge"),
            "payment": payment_body,
        }

    # clover returned an unsuccessful HTTP response
    except requests.HTTPError as e:
        failed_transaction = {
            "timestamp": datetime.now(UTC).isoformat(),
            "amount": float(payment.amount),
            "description": payment.description,
            "status": "failed",
            "error": str(e),
        }
        with open("app/transaction.log", "a") as file:
            file.write(json.dumps(failed_transaction) + "\n")

        raise HTTPException(
            status_code=502, detail="Clover rejected the payment request"
        ) from e
    # unexpected error
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Payment processing failed: {str(e)}"
        )
