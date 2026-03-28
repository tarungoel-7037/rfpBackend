from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import ERROR_MESSAGES, SUCCESS_MESSAGES
from .serializers import (
    AdminSignupSerializer,
    ConfirmOtpResetPasswordSerializer,
    ForgotPasswordSerializer,
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
            serializer.save()
            return Response(
                {"response": "success"},
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
            serializer.save()
            return Response(
                {"response": "success"},
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
                    "response": "success",
                    "user_id": user.id,
                    "type": profile.role if profile else None,
                    "name": f"{user.first_name} {user.last_name}".strip(),
                    "email": user.email,
                    "token": access_token,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "response": "error",
                "error": "Invalid credential",
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
                "response": "success",
                "vendors": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ApproveVendorView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        user_id = request.data.get("user_id")
        status_value = str(request.data.get("status", "")).strip().lower()

        if not user_id or not status_value:
            return Response(
                {
                    "response": "Error",
                    "message": ERROR_MESSAGES["approve_payload_required"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if status_value not in ["approved", "pending"]:
            return Response(
                {
                    "response": "Error",
                    "message": ERROR_MESSAGES["invalid_vendor_status"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        vendor = AccountsUserprofile.objects.filter(
            user_id=user_id,
            role="vendor",
        ).first()

        if not vendor:
            return Response(
                {
                    "response": "Error",
                    "message": ERROR_MESSAGES["vendor_not_found"],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if status_value == "approved":
            if int(vendor.is_vendor_approved) == 1 and (vendor.status or "").strip().lower() == "active":
                return Response(
                    {
                        "response": "Error",
                        "message": ERROR_MESSAGES["already_approved"],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            vendor.is_vendor_approved = 1
            vendor.status = "active"
            success_message = SUCCESS_MESSAGES["vendor_approved"]
        else:
            if int(vendor.is_vendor_approved) == 0 and (vendor.status or "").strip().lower() == "pending":
                return Response(
                    {
                        "response": "Error",
                        "message": ERROR_MESSAGES["already_pending"],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            vendor.is_vendor_approved = 0
            vendor.status = "pending"
            success_message = SUCCESS_MESSAGES["vendor_disapproved"]

        vendor.updated_at = timezone.now()
        vendor.save(update_fields=["is_vendor_approved", "status", "updated_at"])

        return Response(
            {
                "response": "success",
                "message": success_message,
            },
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "response": "success",
                    "message": SUCCESS_MESSAGES["otp_sent"],
                },
                status=status.HTTP_200_OK,
            )

        error_text = serializer.errors.get("email", [None])[0]
        return Response(
            {
                "response": "error",
                "message": error_text or ERROR_MESSAGES["email_not_found"],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ConfirmOtpResetPasswordView(APIView):
    def post(self, request):
        serializer = ConfirmOtpResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "response": "success",
                    "message": SUCCESS_MESSAGES["password_reset"],
                },
                status=status.HTTP_200_OK,
            )

        error_text = serializer.errors.get("non_field_errors", [None])[0]
        if not error_text:
            for field_errors in serializer.errors.values():
                if isinstance(field_errors, list) and field_errors:
                    error_text = str(field_errors[0])
                    break

        return Response(
            {
                "response": "error",
                "message": error_text or "Invalid data.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
