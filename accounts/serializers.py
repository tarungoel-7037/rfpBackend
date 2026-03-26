import re

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import serializers

from .constants import ERROR_MESSAGES
from rfp.models import AccountsUserprofile, AuthUser, RfpCategory


class AdminSignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20)

    def validate_email(self, value):
        email = value.strip().lower()
        if AuthUser.objects.filter(username=email).exists():
            raise serializers.ValidationError(ERROR_MESSAGES["user_exists"])
        return email

    def create(self, validated_data):
        now = timezone.now()

        user = AuthUser.objects.create(
            username=validated_data["email"],
            first_name=validated_data["first_name"].strip(),
            last_name=validated_data["last_name"].strip(),
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            is_superuser=0,
            is_staff=1,
            is_active=1,
            date_joined=now,
            last_login=None,
        )

        AccountsUserprofile.objects.create(
            user=user,
            role="admin",
            phone=validated_data["phone"].strip(),
            company_name=None,
            is_vendor_approved=1,
            created_at=now,
            updated_at=now,
            category=None,
            gst_no=None,
            no_of_employees=None,
            pancard_no=None,
            revenue=None,
            status="active",
        )

        return user


class VendorSignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20)
    revenue = serializers.CharField(max_length=255)
    no_of_employees = serializers.CharField(max_length=10)
    gst_no = serializers.CharField(max_length=20)
    pan_no = serializers.CharField(max_length=20)
    category = serializers.CharField(max_length=10)

    def validate_email(self, value):
        email = value.strip().lower()
        if AuthUser.objects.filter(username=email).exists():
            raise serializers.ValidationError(ERROR_MESSAGES["user_exists"])
        return email

    def validate_category(self, value):
        category = value.strip()
        category_exists = (
            RfpCategory.objects.filter(id=category).exists()
            or RfpCategory.objects.filter(name=category).exists()
        )

        if not category_exists:
            raise serializers.ValidationError(ERROR_MESSAGES["invalid_category"])

        return category

    def validate_gst_no(self, value):
        gst_no = value.strip().upper()
        gst_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$"

        if not re.match(gst_pattern, gst_no):
            raise serializers.ValidationError(ERROR_MESSAGES["invalid_gst"])

        return gst_no

    def validate_pan_no(self, value):
        pan_no = value.strip().upper()
        pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"

        if not re.match(pan_pattern, pan_no):
            raise serializers.ValidationError(ERROR_MESSAGES["invalid_pan"])

        return pan_no

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": ERROR_MESSAGES["password_mismatch"]}
            )
        return attrs

    def create(self, validated_data):
        now = timezone.now()
        validated_data.pop("confirm_password")

        user = AuthUser.objects.create(
            username=validated_data["email"],
            first_name=validated_data["first_name"].strip(),
            last_name=validated_data["last_name"].strip(),
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            is_superuser=0,
            is_staff=0,
            is_active=1,
            date_joined=now,
            last_login=None,
        )

        AccountsUserprofile.objects.create(
            user=user,
            role="vendor",
            phone=validated_data["phone"].strip(),
            company_name=None,
            is_vendor_approved=0,
            created_at=now,
            updated_at=now,
            category=validated_data["category"],
            gst_no=validated_data["gst_no"].strip(),
            no_of_employees=validated_data["no_of_employees"].strip(),
            pancard_no=validated_data["pan_no"].strip(),
            revenue=validated_data["revenue"].strip(),
            status="pending",
        )

        return user
