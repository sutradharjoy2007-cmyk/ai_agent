from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """Custom user model with email as username"""
    username = None
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    def get_email_prefix(self):
        """Get the part of email before @ symbol"""
        return self.email.split('@')[0] if '@' in self.email else self.email


class UserProfile(models.Model):
    """User profile with additional information"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    home_address = models.TextField(blank=True)
    
    # KYC Fields
    KYC_STATUS_CHOICES = (
        ('NONE', 'Not Submitted'),
        ('PENDING', 'Under Review'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    )
    kyc_document = models.ImageField(upload_to='kyc_documents/', blank=True, null=True)
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='NONE')
    
    # Subscription fields
    subscription_expiry = models.DateTimeField(null=True, blank=True)
    package_name = models.CharField(max_length=50, blank=True, default='Free Trial')
    
    def __str__(self):
        return f"{self.user.email}'s profile"
    
    def is_subscription_active(self):
        """Check if subscription is active"""
        from django.utils import timezone
        if not self.subscription_expiry:
            return True # Allow access if no expiry set (or change logic as needed)
        return timezone.now() < self.subscription_expiry


class AIAgentConfig(models.Model):
    """AI Agent configuration for each user"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='ai_config')
    facebook_page_id = models.CharField(max_length=2000, blank=True)
    facebook_page_api= models.CharField(max_length=2000, blank=True)
    system_prompt = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.email}'s AI config"
    
    def get_webhook_url(self):
        """Generate webhook URL based on user's email"""
        email_prefix = self.user.get_email_prefix()
        return f"https://ftn8nbd.onrender.com/webhook/{email_prefix}"
