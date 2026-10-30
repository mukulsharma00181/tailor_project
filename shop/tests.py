from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Order
from .payments import build_upi_link

try:
    import segno  # noqa: F401
    HAS_SEGNO = True
except ImportError:
    HAS_SEGNO = False


class PaymentQRTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user("owner", password="pw12345!", is_staff=True)
        self.client.login(username="owner", password="pw12345!")

    def make_order(self, **kw):
        data = dict(customer_name="Ravi", shirt_qty=2, shirt_price=500,
                    pant_qty=1, pant_price=700, amount_paid=200,
                    status=Order.Status.READY)
        data.update(kw)
        return Order.objects.create(**data)

    def test_upi_link_uses_balance_due(self):
        order = self.make_order()  # total 1700, paid 200 -> 1500 due
        q = parse_qs(urlparse(build_upi_link(order)).query)
        self.assertEqual(q["am"], ["1500.00"])
        self.assertEqual(q["cu"], ["INR"])
        self.assertEqual(q["tn"], [f"Order {order.order_no}"])

    def test_qr_card_only_when_ready(self):
        order = self.make_order(status=Order.Status.STITCHING)
        resp = self.client.get(reverse("order_detail", args=[order.pk]))
        self.assertNotContains(resp, "Payment QR")

    def test_qr_card_when_ready(self):
        order = self.make_order()
        resp = self.client.get(reverse("order_detail", args=[order.pk]))
        self.assertContains(resp, "Payment QR")
        self.assertContains(resp, "₹1500")
        if HAS_SEGNO:
            self.assertContains(resp, "data:image/svg+xml;base64,")

    def test_ready_but_fully_paid(self):
        order = self.make_order(amount_paid=1700)
        resp = self.client.get(reverse("order_detail", args=[order.pk]))
        self.assertContains(resp, "Fully paid")

    def test_pay_button_in_list(self):
        self.make_order()
        resp = self.client.get(reverse("order_list"))
        self.assertContains(resp, "Pay QR")

    def test_login_required(self):
        order = self.make_order()
        self.client.logout()
        resp = self.client.get(reverse("order_detail", args=[order.pk]))
        self.assertEqual(resp.status_code, 302)
