from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rfpBackend.permissions import IsAdminRole

from .constants import RFP_MESSAGES
from .models import AccountsUserprofile, RfpRfp
from .serializers import CreateRfpSerializer, RfpListSerializer, VendorByCategorySerializer


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
