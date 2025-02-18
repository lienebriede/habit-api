from django.contrib import admin
from django.utils.html import format_html
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at', 'updated_at', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        """Displays an image preview in the Django admin panel."""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%"/>', obj.image.url)
        return "(No image)"

    image_preview.short_description = "Profile Image"

admin.site.register(Profile, ProfileAdmin)