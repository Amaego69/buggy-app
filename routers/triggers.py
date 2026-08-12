"""Trigger endpoints that intentionally raise the three demo bugs."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from models import DiscountRequest
from services import (
    calculate_discounted_total,
    checkout_empty_cart,
    get_async_price_summary,
)

router = APIRouter(prefix="/trigger", tags=["triggers"])


class EmptyCartCheckoutBody(BaseModel):
    user_id: int = Field(default=1, ge=1)


class InvalidDiscountBody(BaseModel):
    price: str = Field(default="99.99", description="Price as string from external API")
    discount_percent: int = Field(default=10, ge=0, le=100)
    coupon_code: str | None = "WELCOME10"


@router.post("/empty-cart-checkout")
def trigger_empty_cart_checkout(body: EmptyCartCheckoutBody | None = None):
    """
    Trigger Bug 1 — IndexError.

    Checks out with an empty cart; find_cheapest_item accesses items[0].
    """
    payload = body or EmptyCartCheckoutBody()
    try:
        return checkout_empty_cart(payload.user_id)
    except IndexError:
        raise HTTPException(status_code=400, detail="Cart is empty; cannot determine cheapest item.")


@router.post("/invalid-discount-type")
def trigger_invalid_discount_type(body: InvalidDiscountBody | None = None):
    """
    Bug 2 (fixed) — price arrives as a string from an external pricing API,
    but is now safely converted to a numeric type before arithmetic.
    """
    payload = body or InvalidDiscountBody()
    request = DiscountRequest(
        price=payload.price,
        discount_percent=payload.discount_percent,
        coupon_code=payload.coupon_code,
    )
    try:
        return calculate_discounted_total(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/async-price-fetch")
async def trigger_async_price_fetch(product_id: int = 1):
    """
    Bug 3 (fixed) — properly awaits the coroutine so price is a float.
    """
    try:
        return await get_async_price_summary(product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
