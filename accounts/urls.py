from django.urls import path

from .views import AdminSignupView, VendorSignupView


urlpatterns = [
    path("signup/admin/", AdminSignupView.as_view(), name="admin-signup"),
    path("signup/vendor/", VendorSignupView.as_view(), name="vendor-signup"),
]
