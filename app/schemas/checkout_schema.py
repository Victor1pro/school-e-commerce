# app/schemas/checkout_schema.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class CheckoutRequest(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    address: str
    city: str
    postcode: str

    # Payment fields (not stored, only validated)
    card_number: str = Field(..., min_length=12, max_length=19)
    expiry: str = Field(..., min_length=4, max_length=5)
    cvv: str = Field(..., min_length=3, max_length=4)