from django.urls import path

from .views import CreateRfpView, RfpListView, VendorsByCategoryView


urlpatterns = [
    path("createrfp/", CreateRfpView.as_view(), name="create-rfp"),
    path("rfp/all/", RfpListView.as_view(), name="get-rfp"),
    path("vendorlist/<int:category_id>/", VendorsByCategoryView.as_view(), name="vendors-by-category"),
]
