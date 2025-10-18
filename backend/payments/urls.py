from django.urls import path
from .views import OrderCreateView, PaymentCreateView

urlpatterns = [
    path("orders/", OrderCreateView.as_view(), name="orders-create"),
    path("create-payment/", PaymentCreateView.as_view(), name="payments-create"),
]
