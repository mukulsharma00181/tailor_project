from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, Q, Sum
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import OrderForm
from .models import Order
from .payments import build_upi_link, make_qr_data_uri


def home(request):
    """Public page: price list + billing calculator."""
    return render(request, "index.html")


class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only a logged-in owner (staff / superuser) may use the order pages."""

    def test_func(self):
        return self.request.user.is_staff


class OrderListView(OwnerRequiredMixin, ListView):
    model = Order
    template_name = "shop/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        qs = Order.objects.all()
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "")
        if q:
            qs = qs.filter(Q(customer_name__icontains=q) | Q(mobile__icontains=q))
        if status in Order.Status.values:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["qs"] = params.urlencode()
        ctx["q"] = self.request.GET.get("q", "")
        ctx["current_status"] = self.request.GET.get("status", "")
        ctx["status_choices"] = Order.Status.choices

        everything = Order.objects.all()
        sums = everything.aggregate(
            billed=Sum(F("shirt_qty") * F("shirt_price") + F("pant_qty") * F("pant_price")),
            paid=Sum("amount_paid"),
        )
        billed = sums["billed"] or 0
        paid = sums["paid"] or 0
        ctx["stats"] = {
            "orders": everything.count(),
            "open": everything.exclude(status=Order.Status.DELIVERED).count(),
            "billed": billed,
            "paid": paid,
            "due": max(billed - paid, 0),
        }
        return ctx


class OrderDetailView(OwnerRequiredMixin, DetailView):
    model = Order
    template_name = "shop/order_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order = self.object

        # Payment QR is only offered once the order is Ready.
        ctx["show_qr"] = order.status == Order.Status.READY
        if ctx["show_qr"] and order.balance > 0:
            link = build_upi_link(order)
            ctx["upi_link"] = link
            ctx["upi_id"] = settings.UPI_ID
            try:
                ctx["qr_uri"] = make_qr_data_uri(link)
            except ImportError:
                ctx["qr_missing"] = True
        return ctx


class OrderCreateView(OwnerRequiredMixin, SuccessMessageMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "shop/order_form.html"
    success_url = reverse_lazy("order_list")
    success_message = "Order for %(customer_name)s was saved."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "New Order"
        return ctx


class OrderUpdateView(OwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "shop/order_form.html"
    success_url = reverse_lazy("order_list")
    success_message = "Order for %(customer_name)s was updated."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"Edit Order #{self.object.order_no}"
        return ctx


class OrderDeleteView(OwnerRequiredMixin, DeleteView):
    model = Order
    template_name = "shop/order_confirm_delete.html"
    success_url = reverse_lazy("order_list")

    def form_valid(self, form):
        name = self.object.customer_name
        response = super().form_valid(form)
        messages.success(self.request, f"Order for {name} was deleted.")
        return response
