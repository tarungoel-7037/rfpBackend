from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import SUCCESS_MESSAGES
from .serializers import AdminSignupSerializer, VendorSignupSerializer


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
