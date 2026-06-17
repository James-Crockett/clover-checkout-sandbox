from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
    amount: float = Field(gt=0)                 # amount should always be +ve and greater than 0.
    description: str = Field(min_length=1)      # cannot be an empty string

@app.get("/")
def root():
    return {
        "message": "Payment backend running"
    }

@app.post("/api/payments")
def create_payment(payment: PaymentRequest):

    cent_conv = int(payment.amount * 100)       # converting amount to int and cents

    #recording transaction
    transaction = {
        "timestamp": datetime.utcnow().isoformat(),   
        "amount": payment.amount,
        "amt_conv_format": cent_conv,
        "description": payment.description,
        "status": "SUCCESS"  
    }

    with open("apt/transaction.log","a") as file:   #logging transaxtion
        file.write(json.dumps(transaction) + "\n")

    return{
        "success": True,
        "status":"SUCCESS",
        "amount": payment.amount,
        "amt_conv_format": cent_conv,
        "description": payment.description,
        "message": "Payment endpoint working and transaction logged"
    }