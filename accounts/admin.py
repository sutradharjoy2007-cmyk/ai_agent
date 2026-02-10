from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, UserProfile, AIAgentConfig


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ['email']
    ordering = ['email']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'kyc_status', 'kyc_document_link', 'subscription_expiry', 'package_name']
    list_filter = ['kyc_status', 'package_name']
    actions = ['approve_kyc', 'reject_kyc', 'assign_7_days', 'assign_15_days', 'assign_30_days']
    readonly_fields = ['kyc_document_preview']
    
    def kyc_document_link(self, obj):
        from django.utils.html import format_html
        if obj.kyc_document:
            return format_html('<a href="{}" target="_blank">View Document</a>', obj.kyc_document.url)
        return "No document"
    kyc_document_link.short_description = "KYC Document"
    
    def kyc_document_preview(self, obj):
        from django.utils.html import format_html
        if obj.kyc_document:
            return format_html('<img src="{}" style="max-width:400px; max-height:300px;" />', obj.kyc_document.url)
        return "No document uploaded"
    kyc_document_preview.short_description = "KYC Document Preview"
    
    @admin.action(description="✅ Approve KYC Verification")
    def approve_kyc(self, request, queryset):
        updated_count = queryset.update(kyc_status='VERIFIED')
        
        # Send approval emails
        for profile in queryset:
            try:
                send_mail(
                    subject='KYC Verification Approved',
                    message=f'Dear {profile.name},\n\nYour KYC verification has been approved. You now have full access to all AI Agent features.\n\nBest regards,\nAI Agent Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[profile.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send approval email to {profile.user.email}: {e}")

        self.message_user(request, f"{updated_count} users have been verified.")
    approve_kyc.short_description = "✅ Approve KYC Verification"
    
    @admin.action(description="❌ Reject KYC Verification")
    def reject_kyc(self, request, queryset):
        updated_count = queryset.update(kyc_status='REJECTED')
        
        # Send rejection emails
        for profile in queryset:
            try:
                send_mail(
                    subject='KYC Verification Rejected',
                    message=f'Dear {profile.name},\n\nYour KYC document was rejected. Please log in to your profile and upload a valid document (NID or Passport).\n\nBest regards,\nAI Agent Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[profile.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send rejection email to {profile.user.email}: {e}")

        self.message_user(request, f"{updated_count} users have been rejected.")
    reject_kyc.short_description = "❌ Reject KYC Verification"
    
    def assign_days(self, request, queryset, days, package_name):
        from django.utils import timezone
        from datetime import timedelta
        
        expiry_date = timezone.now() + timedelta(days=days)
        updated_count = queryset.update(
            subscription_expiry=expiry_date,
            package_name=package_name
        )
        self.message_user(request, f"{updated_count} users assigned {package_name} package.")
    
    @admin.action(description="Assign 7 Days Package")
    def assign_7_days(self, request, queryset):
        self.assign_days(request, queryset, 7, "7 Days Pack")
    
    @admin.action(description="Assign 15 Days Package")
    def assign_15_days(self, request, queryset):
        self.assign_days(request, queryset, 15, "15 Days Pack")
    
    @admin.action(description="Assign 30 Days Package")
    def assign_30_days(self, request, queryset):
        self.assign_days(request, queryset, 30, "30 Days Pack")


admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(UserProfile) # Replaced with custom admin class
admin.site.register(AIAgentConfig)
