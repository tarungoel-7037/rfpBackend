from django.urls import path

from .views import CloseRfpView, CreateRfpView, RfpListView, VendorsByCategoryView


urlpatterns = [
    path("createrfp/", CreateRfpView.as_view(), name="create-rfp"),
    path("rfp/all/", RfpListView.as_view(), name="get-rfp"),
    path("rfp/closerfp/<int:rfp_id>/", CloseRfpView.as_view(), name="close-rfp"),
    path("vendorlist/<int:category_id>/", VendorsByCategoryView.as_view(), name="vendors-by-category"),
]
