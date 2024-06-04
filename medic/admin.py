# Register your models here.
from django.contrib import admin
from .models import Location, Medic, Review, IdentityVerification, Expertise, Tag, Feedback, SocialAuthData, Booking
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude']

@admin.register(Medic)
class MedicAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'email', 'phone_number', 'verified', 'created_at', 'updated_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [ 'medic', 'status', 'social_user', 'default_user', 'rating']

@admin.register(IdentityVerification)
class IdentityVerificationAdmin(admin.ModelAdmin):
    list_display = ['medic', 'verified', 'verified_at']

@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']

@admin.register(SocialAuthData)
class SocialAuthDataAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'email']

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        # Remove this line if you do not have date_joined field
        # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Important dates'), {'fields': ('last_login',)}),  # Adjusted
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'id', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['medic', 'patient', 'status', 'created_at', 'updated_at', 'id']