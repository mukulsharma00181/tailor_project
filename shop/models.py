from django.db import models


class Order(models.Model):
    """One customer order (shirts + pants) with measurements and payment info."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        STITCHING = "stitching", "Stitching"
        READY = "ready", "Ready"
        DELIVERED = "delivered", "Delivered"

    # Customer
    customer_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, blank=True)

    # Items
    shirt_qty = models.PositiveIntegerField(default=0)
    shirt_price = models.PositiveIntegerField(default=500)
    pant_qty = models.PositiveIntegerField(default=0)
    pant_price = models.PositiveIntegerField(default=700)

    # Measurements (inches)
    chest = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    length = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    waist = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    shoulder = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    # Work + payment
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    amount_paid = models.PositiveIntegerField(default=0)
    delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.order_no} {self.customer_name}"

    @property
    def order_no(self):
        # First order is 500, same as the serial number on the public page.
        return 499 + self.pk if self.pk else None

    @property
    def shirt_total(self):
        return self.shirt_qty * self.shirt_price

    @property
    def pant_total(self):
        return self.pant_qty * self.pant_price

    @property
    def total(self):
        return self.shirt_total + self.pant_total

    @property
    def balance(self):
        return max(self.total - self.amount_paid, 0)

    @property
    def is_paid(self):
        return self.balance == 0 and self.total > 0
