from django.urls import path

from .views import CloseRfpView, CreateRfpView, RfpListView, VendorRfpListView, VendorsByCategoryView


urlpatterns = [
    path("createrfp/", CreateRfpView.as_view(), name="create-rfp"),
    path("rfp/all/", RfpListView.as_view(), name="get-rfp"),
    path("rfp/getrfp/<int:vendor_id>/", VendorRfpListView.as_view(), name="vendor-rfp-list"),
    path("rfp/closerfp/<int:rfp_id>/", CloseRfpView.as_view(), name="close-rfp"),
    path("vendorlist/<int:category_id>/", VendorsByCategoryView.as_view(), name="vendors-by-category"),
]
