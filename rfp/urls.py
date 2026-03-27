from django.urls import path

from .views import CloseRfpView, CreateRfpView, QuoteDetailView, RfpListView, SubmitQuoteView, VendorRfpListView, VendorsByCategoryView


urlpatterns = [
    path("createrfp/", CreateRfpView.as_view(), name="create-rfp"),
    path("rfp/all/", RfpListView.as_view(), name="get-rfp"),
    path("rfp/getrfp/<int:vendor_id>/", VendorRfpListView.as_view(), name="vendor-rfp-list"),
    path("rfp/quotes/<int:rfp_id>/", QuoteDetailView.as_view(), name="quote-detail"),
    path("rfp/closerfp/<int:rfp_id>/", CloseRfpView.as_view(), name="close-rfp"),
    path("rfp/apply/<int:rfp_id>/", SubmitQuoteView.as_view(), name="submit-quote"),
    path("vendorlist/<int:category_id>/", VendorsByCategoryView.as_view(), name="vendors-by-category"),
]
