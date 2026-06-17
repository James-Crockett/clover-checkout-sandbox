from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

from app.clover_service import create_order, add_line_item

app = FastAPI()

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