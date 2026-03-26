from django.contrib import admin

from .models import AccountsUserprofile, AuthUser


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "is_superuser",
        "date_joined",
    )
    search_fields = ("username", "first_name", "last_name", "email")
    list_filter = ("is_staff", "is_active", "is_superuser")


@admin.register(AccountsUserprofile)
class AccountsUserprofileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "role",
        "phone",
        "category",
        "gst_no",
        "pancard_no",
        "status",
        "is_vendor_approved",
    )
    search_fields = ("user__username", "user__email", "phone", "gst_no", "pancard_no")
    list_filter = ("role", "status", "is_vendor_approved")
