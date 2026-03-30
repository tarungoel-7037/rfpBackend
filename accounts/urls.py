from django.urls import path

from .views import (
    AdminSignupView,
    ApproveVendorView,
    ConfirmOtpResetPasswordView,
    ForgotPasswordView,
    LoginView,
    VendorListView,
    VendorSignupView,
)


urlpatterns = [
    path("forgetPassword/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("confirmotpresetPassword/", ConfirmOtpResetPasswordView.as_view(), name="confirm-otp-reset-password"),
    path("registeradmin/", AdminSignupView.as_view(), name="admin-signup"),
    path("registervendor/", VendorSignupView.as_view(), name="vendor-signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("vendorlist/", VendorListView.as_view(), name="vendor-list"),
    path("approveVendor/", ApproveVendorView.as_view(), name="approve-vendor"),
    path("vendors/<int:user_id>/disapprove/", ApproveVendorView.as_view(), {"action": "disapprove"}, name="disapprove-vendor-by-id"),
]
