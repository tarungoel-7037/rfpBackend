from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import CATEGORY_MESSAGES
from .serializers import CategorySerializer
from rfpBackend.permissions import IsAdminRole
from rfp.models import RfpCategory


class CategoryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminRole()]

    def get(self, request):
        categories = RfpCategory.objects.all().order_by("name")
        serializer = CategorySerializer(categories, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": CATEGORY_MESSAGES["created"],
                    "data": serializer.data,
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


class CategoryDetailView(APIView):
    permission_classes = [IsAdminRole]

    def get_object(self, category_id):
        return RfpCategory.objects.filter(id=category_id).first()

    def get(self, request, category_id):
        category = self.get_object(category_id)
        if not category:
            return Response(
                {
                    "success": False,
                    "message": CATEGORY_MESSAGES["not_found"],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CategorySerializer(category)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, category_id):
        category = self.get_object(category_id)
        if not category:
            return Response(
                {
                    "success": False,
                    "message": CATEGORY_MESSAGES["not_found"],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": CATEGORY_MESSAGES["updated"],
                    "data": serializer.data,
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

    def delete(self, request, category_id):
        category = self.get_object(category_id)
        if not category:
            return Response(
                {
                    "success": False,
                    "message": CATEGORY_MESSAGES["not_found"],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        category.delete()
        return Response(
            {
                "success": True,
                "message": CATEGORY_MESSAGES["deleted"],
            },
            status=status.HTTP_200_OK,
        )
