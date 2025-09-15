from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from Authentication.models import User


# Register your models here.


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Các field sẽ hiển thị trong list view
    list_display = ("email", "username", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")

    # Cho phép tìm kiếm theo email và username
    search_fields = ("email", "username")
    ordering = ("email",)

    # Cấu hình giao diện khi vào form chỉnh sửa user
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Thông tin cá nhân", {"fields": ("first_name", "last_name", "text", "role")}),
        ("Phân quyền", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Thời gian", {"fields": ("last_login", "date_joined")}),
    )

    # Cấu hình khi tạo user mới trong admin
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )