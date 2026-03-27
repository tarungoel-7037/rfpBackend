import re

from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework import serializers

from .constants import ERROR_MESSAGES
from .utils import send_registration_email
from rfp.models import AccountsUserprofile, AuthUser, RfpCategory


class AdminSignupSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=150)
    lastname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    mobile = serializers.CharField(max_length=20)

    def validate_email(self, value):
        email = value.strip().lower()
        if AuthUser.objects.filter(username=email).exists():
            raise serializers.ValidationError(ERROR_MESSAGES["user_exists"])
        return email

    def create(self, validated_data):
        now = timezone.now()

        user = AuthUser.objects.create(
            username=validated_data["email"],
            first_name=validated_data["firstname"].strip(),
            last_name=validated_data["lastname"].strip(),
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
            phone=validated_data["mobile"].strip(),
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

        send_registration_email(user, "admin")
        return user


class VendorSignupSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=150)
    lastname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    mobile = serializers.CharField(max_length=20)
    revenue = serializers.CharField(max_length=255)
    no_of_employees = serializers.CharField(max_length=10)
    gst_no = serializers.CharField(max_length=20)
    pancard_no = serializers.CharField(max_length=20)
    category = serializers.CharField()

    def validate_email(self, value):
        email = value.strip().lower()
        if AuthUser.objects.filter(username=email).exists():
            raise serializers.ValidationError(ERROR_MESSAGES["user_exists"])
        return email

    def validate_gst_no(self, value):
        gst_no = value.strip().upper()
        gst_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$"

        if not re.match(gst_pattern, gst_no):
            raise serializers.ValidationError(ERROR_MESSAGES["invalid_gst"])

        return gst_no

    def validate_pancard_no(self, value):
        pan_no = value.strip().upper()
        pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"

        if not re.match(pan_pattern, pan_no):
            raise serializers.ValidationError(ERROR_MESSAGES["invalid_pan"])

        return pan_no

    def create(self, validated_data):
        now = timezone.now()

        user = AuthUser.objects.create(
            username=validated_data["email"],
            first_name=validated_data["firstname"].strip(),
            last_name=validated_data["lastname"].strip(),
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
            phone=validated_data["mobile"].strip(),
            company_name=None,
            is_vendor_approved=0,
            created_at=now,
            updated_at=now,
            category=validated_data["category"],
            gst_no=validated_data["gst_no"].strip(),
            no_of_employees=validated_data["no_of_employees"].strip(),
            pancard_no=validated_data["pancard_no"].strip(),
            revenue=validated_data["revenue"].strip(),
            status="pending",
        )

        send_registration_email(user, "vendor")
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        password = attrs["password"]

        try:
            user = AuthUser.objects.get(username=email)
        except AuthUser.DoesNotExist:
            raise serializers.ValidationError(ERROR_MESSAGES["invalid_credentials"])

        if int(user.is_active) != 1:
            raise serializers.ValidationError(ERROR_MESSAGES["inactive_user"])

        if not check_password(password, user.password):
            raise serializers.ValidationError(ERROR_MESSAGES["invalid_credentials"])

        attrs["email"] = email
        attrs["user"] = user
        return attrs


class VendorListSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(source="user.id")
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email")
    mobile = serializers.CharField(source="phone")
    no_of_employees = serializers.CharField()
    status = serializers.SerializerMethodField()
    categories = serializers.CharField(source="category")

    def get_name(self, obj):
        first_name = (obj.user.first_name or "").strip()
        last_name = (obj.user.last_name or "").strip()
        return f"{first_name} {last_name}".strip()

    def get_status(self, obj):
        status_value = (obj.status or "").strip().lower()

        if status_value == "active":
            return "Approved"
        if status_value == "disapproved":
            return "Disapproved"
        if status_value == "pending":
            return "Pending"

        return obj.status
