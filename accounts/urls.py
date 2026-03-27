from django.urls import path

from .views import (
    AdminSignupView,
    ApproveVendorView,
    LoginView,
    VendorListView,
    VendorSignupView,
)


urlpatterns = [
    path("registeradmin/", AdminSignupView.as_view(), name="admin-signup"),
    path("registervendor/", VendorSignupView.as_view(), name="vendor-signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("vendorlist/", VendorListView.as_view(), name="vendor-list"),
    path("approveVendor/", ApproveVendorView.as_view(), name="approve-vendor"),
]
