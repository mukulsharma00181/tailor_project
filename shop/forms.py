from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "customer_name", "mobile",
            "shirt_qty", "shirt_price", "pant_qty", "pant_price",
            "chest", "length", "waist", "shoulder",
            "status", "amount_paid", "delivery_date", "notes",
        ]
        widgets = {
            "delivery_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "chest": forms.NumberInput(attrs={"step": "0.1", "min": "0"}),
            "length": forms.NumberInput(attrs={"step": "0.1", "min": "0"}),
            "waist": forms.NumberInput(attrs={"step": "0.1", "min": "0"}),
            "shoulder": forms.NumberInput(attrs={"step": "0.1", "min": "0"}),
        }

    def clean(self):
        data = super().clean()
        keys = ("shirt_qty", "shirt_price", "pant_qty", "pant_price", "amount_paid")
        values = [data.get(k) for k in keys]
        if any(v is None for v in values):
            return data  # field-level errors are already showing

        shirt_qty, shirt_price, pant_qty, pant_price, paid = values
        total = shirt_qty * shirt_price + pant_qty * pant_price

        if shirt_qty + pant_qty == 0:
            raise forms.ValidationError("Add at least one shirt or pant.")
        if paid > total:
            raise forms.ValidationError(
                f"Amount paid (₹{paid}) cannot be more than the total (₹{total})."
            )
        return data
