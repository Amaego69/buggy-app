"""Utility helpers for cart and price calculations."""

from models import CartItem


def format_currency(amount: float) -> str:
    return f"${amount:.2f}"


def find_cheapest_item(items: list[CartItem]) -> CartItem:
    """
    Return the cheapest item in the cart.

    BUG 1 — IndexError: assumes the cart is never empty and indexes items[0]
    without a guard. Calling this with an empty list raises IndexError.
    """
    cheapest = items[0]
    for item in items[1:]:
        if item.price < cheapest.price:
            cheapest = item
    return cheapest


def apply_percent_discount(price, discount_percent: int) -> float:
    """
    Apply a percentage discount to a price.

    BUG 2 — TypeError: when `price` is a string (as returned by an external
    pricing API), subtracting a float from a str fails at runtime.
    """
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount
