from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission  
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        verbose_name=_('groups'),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
    
class SocialAuthData(models.Model):
    social_user_id = models.CharField(max_length=255)
    provider = models.CharField(max_length=50)
    email = models.EmailField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    picture = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Add more fields as needed to capture additional user attributes

    def __str__(self):
        return f"{self.name} - {self.provider}"

class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class Medic(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, related_name='medic', on_delete=models.CASCADE, null=True, blank=True)
    picture = models.ImageField(upload_to='pictures/')
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    description = models.TextField()
    location = models.ForeignKey('Location', related_name='location', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    verified = models.BooleanField(default=False)
    expertise = models.ManyToManyField('Expertise', related_name='expertise')
    available = models.BooleanField(default=True)
    area_coverage_km = models.FloatField(blank=True, null=True, help_text="Coverage radius in kilometers")
    extra_fields = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('pending', 'Pending'),
    )
     
    medic = models.ForeignKey(Medic, related_name='review_items', on_delete=models.CASCADE)
    social_user = models.ForeignKey(SocialAuthData, on_delete=models.CASCADE, null=True, blank=True)
    default_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rating = models.FloatField()
    tags = models.ManyToManyField('Tag', blank=True)
    extra_fields = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.medic.name} for Medic: {self.medic.name}"

class IdentityVerification(models.Model):
    medic = models.OneToOneField(Medic, related_name='identity_verification', on_delete=models.CASCADE)
    document = models.ImageField(upload_to='identity_verification/')
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    extra_fields = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Identity Verification for {self.medic.name}"

class Expertise(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username if self.user else 'Anonymous'}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('location_shared', 'Location Shared'),
        ('otp_sent', 'OTP Sent'),
        ('in_progress', 'In Progress'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    patient = models.ForeignKey(CustomUser, related_name='patient_bookings', on_delete=models.CASCADE)
    medic = models.ForeignKey(Medic, related_name='medic_bookings', on_delete=models.CASCADE)
    care_type = models.ForeignKey(Expertise, related_name='care_type', on_delete=models.CASCADE, null=True, blank=True)
    otp = models.CharField(max_length=4, null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    extra_fields = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    timeout_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Booking from {self.patient.email} to {self.medic.name} ({self.medic.email})"
