from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import ERROR_MESSAGES, SUCCESS_MESSAGES
from .serializers import AdminSignupSerializer, LoginSerializer, VendorSignupSerializer
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
