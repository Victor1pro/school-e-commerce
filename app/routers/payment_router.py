from fastapi import APIRouter, Depends


# CREATES PAYMNET ROUTE
router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)