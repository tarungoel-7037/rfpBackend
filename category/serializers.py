from django.utils import timezone
from rest_framework import serializers

from rfp.models import RfpCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RfpCategory
        fields = ["id", "name", "description", "created_at", "status"]
        read_only_fields = ["id", "description", "created_at", "status"]

    def create(self, validated_data):
        validated_data["description"] = None
        validated_data["created_at"] = timezone.now()
        validated_data["status"] = "active"
        return RfpCategory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        RfpCategory.objects.filter(pk=instance.pk).update(**validated_data)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        return instance
