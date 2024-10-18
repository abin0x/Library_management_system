from django.contrib import admin
from .models import CustomUser,User,UserManager

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('user_type', 'is_active', 'is_staff')
    ordering = ('username',)
    list_editable = ('is_active', 'is_staff')

    # Optionally, you can make the email field read-only if you do not want it to be editable
    readonly_fields = ('email',)

# Register the CustomUser model with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(User)
