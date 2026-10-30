"""UPI payment link + QR code helpers."""
import base64
import io
from urllib.parse import quote, urlencode

from django.conf import settings


def build_upi_link(order):
    """UPI deep link for the amount still due on this order."""
    params = {
        "pa": settings.UPI_ID,
        "pn": settings.UPI_PAYEE_NAME,
        "am": f"{order.balance:.2f}",
        "cu": "INR",
        "tn": f"Order {order.order_no}",
    }
    return "upi://pay?" + urlencode(params, quote_via=quote)


def make_qr_data_uri(text):
    """Return the QR code for `text` as an SVG data URI (needs the `segno` package)."""
    import segno  # imported here so the site still runs if it is not installed yet

    buffer = io.BytesIO()
    segno.make_qr(text, error="M").save(buffer, kind="svg", scale=6, border=2)
    return "data:image/svg+xml;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
