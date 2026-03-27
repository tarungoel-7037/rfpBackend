from django.utils import timezone
from rest_framework import serializers

from .models import AccountsUserprofile, AuthUser, RfpCategory, RfpRfp, RfpRfpVendors


class VendorByCategorySerializer(serializers.Serializer):
    user_id = serializers.IntegerField(source="user.id")
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email")
    mobile = serializers.CharField(source="phone")

    def get_name(self, obj):
        first_name = (obj.user.first_name or "").strip()
        last_name = (obj.user.last_name or "").strip()
        return f"{first_name} {last_name}".strip()


class RfpListSerializer(serializers.Serializer):
    rfp_id = serializers.IntegerField(source="id")
    admin_id = serializers.IntegerField(source="created_by_id")
    item_name = serializers.CharField()
    item_description = serializers.CharField()
    rfp_no = serializers.CharField()
    quantity = serializers.SerializerMethodField()
    last_date = serializers.SerializerMethodField()
    minimum_price = serializers.SerializerMethodField()
    maximum_price = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    status = serializers.SerializerMethodField()

    def get_quantity(self, obj):
        quantity = obj.quantity
        return int(quantity) if str(quantity).isdigit() else quantity

    def get_last_date(self, obj):
        return obj.last_date.date().isoformat() if obj.last_date else None

    def get_minimum_price(self, obj):
        return int(obj.minimum_price) if obj.minimum_price is not None else None

    def get_maximum_price(self, obj):
        return int(obj.maximum_price) if obj.maximum_price is not None else None

    def get_categories(self, obj):
        return str(obj.category_id) if obj.category_id else None

    def get_status(self, obj):
        status_value = (obj.status or "").strip().lower()
        if status_value == "active":
            return "open"
        return status_value or obj.status


class CreateRfpSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    item_name = serializers.CharField(max_length=255)
    rfp_no = serializers.CharField(max_length=100)
    quantity = serializers.CharField(max_length=50)
    last_date = serializers.DateTimeField()
    minimum_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    maximum_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    categories = serializers.IntegerField()
    vendors = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )
    item_description = serializers.CharField()

    def validate_user_id(self, value):
        if not AuthUser.objects.filter(id=value).exists():
            raise serializers.ValidationError("Select valid User.")
        return value

    def validate_categories(self, value):
        if not RfpCategory.objects.filter(id=value).exists():
            raise serializers.ValidationError("Select valid Category.")
        return value

    def validate_rfp_no(self, value):
        if RfpRfp.objects.filter(rfp_no=value.strip()).exists():
            raise serializers.ValidationError("RFP number already exists.")
        return value.strip()

    def validate(self, attrs):
        if attrs["minimum_price"] > attrs["maximum_price"]:
            raise serializers.ValidationError(
                {"maximum_price": ["Maximum price should be greater than or equal to minimum price."]}
            )

        category_id = str(attrs["categories"])
        valid_vendor_ids = set()
        approved_vendor_profiles = AccountsUserprofile.objects.filter(
            role="vendor",
            is_vendor_approved=1,
        ).select_related("user")

        for profile in approved_vendor_profiles:
            category_value = (profile.category or "").strip()
            category_ids = [item.strip() for item in category_value.split(",") if item.strip()]
            if category_id in category_ids:
                valid_vendor_ids.add(profile.user_id)

        selected_vendor_ids = attrs["vendors"]
        if not selected_vendor_ids or any(vendor_id not in valid_vendor_ids for vendor_id in selected_vendor_ids):
            raise serializers.ValidationError({"vendors": ["Select valid Vendors."]})

        return attrs

    def create(self, validated_data):
        vendor_ids = validated_data.pop("vendors")
        category_id = validated_data.pop("categories")
        user_id = validated_data.pop("user_id")
        now = timezone.now()

        rfp = RfpRfp.objects.create(
            item_description=validated_data["item_description"].strip(),
            maximum_price=validated_data["maximum_price"],
            status="active",
            is_active=1,
            created_at=now,
            updated_at=now,
            category_id=category_id,
            created_by_id=user_id,
            item_name=validated_data["item_name"].strip(),
            last_date=validated_data["last_date"],
            minimum_price=validated_data["minimum_price"],
            quantity=validated_data["quantity"].strip(),
            rfp_no=validated_data["rfp_no"],
        )

        rfp_vendor_links = [
            RfpRfpVendors(rfp_id=rfp.id, user_id=vendor_id)
            for vendor_id in vendor_ids
        ]
        RfpRfpVendors.objects.bulk_create(rfp_vendor_links)

        return rfp
