from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rfpBackend.permissions import IsAdminRole, IsVendorRole

from .constants import RFP_MESSAGES
from .models import AccountsUserprofile, RfpRfp, RfpRfpVendors, RfpRfpquote
from .serializers import CreateRfpSerializer, QuoteDetailSerializer, RfpListSerializer, SubmitQuoteSerializer, VendorByCategorySerializer, VendorRfpListSerializer


class VendorsByCategoryView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, category_id):
        matching_profiles = []
        vendor_profiles = AccountsUserprofile.objects.filter(
            role="vendor",
            is_vendor_approved=1,
        ).select_related("user").order_by("user__first_name", "user__last_name")

        for profile in vendor_profiles:
            category_value = (profile.category or "").strip()
            category_ids = [item.strip() for item in category_value.split(",") if item.strip()]
            if str(category_id) in category_ids:
                matching_profiles.append(profile)

        serializer = VendorByCategorySerializer(matching_profiles, many=True)
        return Response(
            {
                "response": "success",
                "vendors": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CreateRfpView(APIView):
    permission_classes = [IsAdminRole]


    def post(self, request):
        serializer = CreateRfpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"response": "success"},
                status=status.HTTP_201_CREATED,
            )

        if "vendors" in serializer.errors and serializer.errors["vendors"]:
            return Response(
                {
                    "response": "error",
                    "errors": [RFP_MESSAGES["invalid_vendors"]],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        error_list = []
        for field_errors in serializer.errors.values():
            if isinstance(field_errors, list):
                error_list.extend(str(error) for error in field_errors)
            else:
                error_list.append(str(field_errors))

        return Response(
            {
                "response": "error",
                "errors": error_list,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class RfpListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        rfps = RfpRfp.objects.all().order_by("-id")
        serializer = RfpListSerializer(rfps, many=True)
        return Response(
            {
                "response": "success",
                "rfps": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CloseRfpView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, rfp_id):
        rfp = RfpRfp.objects.filter(id=rfp_id).first()
        if not rfp:
            return Response(
                {
                    "response": "error",
                    "message": RFP_MESSAGES["not_found"],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        current_status = (rfp.status or "").strip().lower()
        if current_status == "closed":
            return Response(
                {
                    "response": "error",
                    "message": RFP_MESSAGES["already_closed"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        rfp.status = "closed"
        rfp.save(update_fields=["status"])

        return Response(
            {
                "response": "success",
                "quotes": RFP_MESSAGES["closed"],
            },
            status=status.HTTP_200_OK,
        )


class VendorRfpListView(APIView):
    permission_classes = [IsVendorRole]

    def get(self, request, vendor_id):
        selected_rfp_ids = RfpRfpVendors.objects.filter(
            user_id=vendor_id
        ).values_list("rfp_id", flat=True)

        rfps = RfpRfp.objects.filter(id__in=selected_rfp_ids).order_by("-id")
        vendor_quotes = RfpRfpquote.objects.filter(vendor_id=vendor_id, rfp_id__in=selected_rfp_ids)
        quote_map = {quote.rfp_id: quote for quote in vendor_quotes}
        serializer = VendorRfpListSerializer(
            rfps,
            many=True,
            context={
                "vendor_id": vendor_id,
                "quote_map": quote_map,
            },
        )
        return Response(
            {
                "response": "success",
                "rfps": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class SubmitQuoteView(APIView):
    permission_classes = [IsVendorRole]

    def post(self, request, rfp_id):
        rfp = RfpRfp.objects.filter(id=rfp_id).first()
        if not rfp:
            return Response(
                {
                    "response": "error",
                    "errors": RFP_MESSAGES["not_found"],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = request.data.copy()
        payload.pop("_method", None)

        serializer = SubmitQuoteSerializer(
            data=payload,
            context={
                "rfp": rfp,
                "vendor_id": request.user.id,
            },
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "response": "success",
                    "message": RFP_MESSAGES["quote_submitted"],
                },
                status=status.HTTP_200_OK,
            )

        error_text = serializer.errors.get("non_field_errors", [None])[0]
        if error_text == RFP_MESSAGES["rfp_closed_for_quote"]:
            return Response(
                {
                    "response": "error",
                    "errors": RFP_MESSAGES["rfp_closed_for_quote"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if error_text:
            return Response(
                {
                    "response": "error",
                    "errors": error_text,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        flat_errors = []
        for field_errors in serializer.errors.values():
            if isinstance(field_errors, list):
                flat_errors.extend(str(error) for error in field_errors)
            else:
                flat_errors.append(str(field_errors))

        return Response(
            {
                "response": "error",
                "errors": flat_errors[0] if flat_errors else "Invalid data.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class QuoteDetailView(APIView):
    def get(self, request, rfp_id):
        user = request.user
        if not user or not user.is_authenticated:
            return Response(
                {
                    "response": "error",
                    "message": "Authentication credentials were not provided.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        profile = AccountsUserprofile.objects.filter(user_id=user.id).first()
        is_admin = bool(user.is_staff or user.is_superuser or (profile and profile.role == "admin"))
        is_vendor = bool(profile and profile.role == "vendor")

        if not is_admin and not is_vendor:
            return Response(
                {
                    "response": "error",
                    "message": "You are not authorized to view quotes for this RFP.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if is_admin:
            quotes = RfpRfpquote.objects.filter(rfp_id=rfp_id).select_related("vendor").order_by("-id")
            if not quotes:
                return Response(
                    {
                        "response": "error",
                        "error": RFP_MESSAGES["quote_not_found"],
                    },
                    status=status.HTTP_200_OK,
                )

            serializer = QuoteDetailSerializer(quotes, many=True)
            return Response(
                {
                    "response": "success",
                    "quotes": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        quote = RfpRfpquote.objects.filter(
            rfp_id=rfp_id,
            vendor_id=user.id,
        ).select_related("vendor").first()

        if not quote:
            return Response(
                {
                    "response": "error",
                    "error": RFP_MESSAGES["quote_not_found"],
                },
                status=status.HTTP_200_OK,
            )

        serializer = QuoteDetailSerializer(quote)
        return Response(
            {
                "response": "success",
                "quote": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
