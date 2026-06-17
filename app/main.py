from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

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
    return{
        "success": True,
        "status":"SUCCESS",
        "amount": payment.amount,
        "description": payment.description,
        "message": "Payment endpoint working"
    }