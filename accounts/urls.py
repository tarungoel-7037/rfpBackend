from django.urls import path

from .views import (
    AdminSignupView,
    ApproveVendorView,
    DisapproveVendorView,
    LoginView,
    VendorListView,
    VendorSignupView,
)


urlpatterns = [
    path("signup/admin/", AdminSignupView.as_view(), name="admin-signup"),
    path("signup/vendor/", VendorSignupView.as_view(), name="vendor-signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("vendors/", VendorListView.as_view(), name="vendor-list"),
    path("vendors/<int:user_id>/approve/", ApproveVendorView.as_view(), name="approve-vendor"),
    path("vendors/<int:user_id>/disapprove/", DisapproveVendorView.as_view(), name="disapprove-vendor"),
]
