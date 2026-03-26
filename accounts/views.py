from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import ERROR_MESSAGES, SUCCESS_MESSAGES
from .serializers import (
    AdminSignupSerializer,
    LoginSerializer,
    VendorListSerializer,
    VendorSignupSerializer,
)
from rfpBackend.permissions import IsAdminRole
from rfp.models import AccountsUserprofile


class AdminSignupView(APIView):
    def post(self, request):
        serializer = AdminSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": SUCCESS_MESSAGES["admin_signup"],
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class VendorSignupView(APIView):
    def post(self, request):
        serializer = VendorSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": SUCCESS_MESSAGES["vendor_signup"],
                    "user_id": user.id,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        
        
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            profile = AccountsUserprofile.objects.filter(user=user).first()
            django_user = get_user_model().objects.filter(pk=user.id).first()

            if not django_user:
                return Response(
                    {
                        "success": False,
                        "errors": {
                            "token": [ERROR_MESSAGES["token_user_not_found"]]
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refresh = RefreshToken.for_user(django_user)
            access_token = str(refresh.access_token)

            return Response(
                {
                    "success": True,
                    "message": SUCCESS_MESSAGES["login"],
                    "user_id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": profile.role if profile else None,
                    "status": profile.status if profile else None,
                    "access_token": access_token,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class VendorListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        vendors = AccountsUserprofile.objects.filter(
            role="vendor",
        ).select_related("user").order_by("-created_at")

        serializer = VendorListSerializer(vendors, many=True)

        return Response(
            {
                "success": True,
                "message": SUCCESS_MESSAGES["vendors"],
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ApproveVendorView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, user_id):
        vendor = AccountsUserprofile.objects.filter(
            user_id=user_id,
            role="vendor",
        ).first()

        if not vendor:
            return Response(
                {
                    "success": False,
                    "message": ERROR_MESSAGES["vendor_not_found"],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        vendor.is_vendor_approved = 1
        vendor.status = "active"
        vendor.updated_at = timezone.now()
        vendor.save(update_fields=["is_vendor_approved", "status", "updated_at"])

        return Response(
            {
                "success": True,
                "message": SUCCESS_MESSAGES["vendor_approved"],
            },
            status=status.HTTP_200_OK,
        )


class DisapproveVendorView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, user_id):
        vendor = AccountsUserprofile.objects.filter(
            user_id=user_id,
            role="vendor",
        ).first()

        if not vendor:
            return Response(
                {
                    "success": False,
                    "message": ERROR_MESSAGES["vendor_not_found"],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        vendor.is_vendor_approved = 0
        vendor.status = "disapproved"
        vendor.updated_at = timezone.now()
        vendor.save(update_fields=["is_vendor_approved", "status", "updated_at"])

        return Response(
            {
                "success": True,
                "message": SUCCESS_MESSAGES["vendor_disapproved"],
            },
            status=status.HTTP_200_OK,
        )
