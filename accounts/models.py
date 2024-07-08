from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import secrets


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


def custom_id():
    return secrets.token_urlsafe(8)


class CustomUser(AbstractUser):
    username = None
    userId = models.CharField(max_length=11, unique=True, default=custom_id)
    firstName = models.CharField(max_length=255, null=False)
    lastName = models.CharField(max_length=255, null=False)
    email = models.EmailField(unique=True, null=False)
    phone = models.CharField(max_length=15, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstName", "lastName"]

    def __str__(self):
        return self.firstName


@receiver(post_save, sender=CustomUser)
def create_org(sender, instance, **kwargs):
    if not instance.organisations.exists():  # Ensure it's a new user
        org_name = f"{instance.firstName}'s Organisation"
        org = Organisation.objects.create(name=org_name)
        org.users.add(instance)
        org.save()


class OrganizationManager(models.Manager):
    def for_user(self, user):
        return self.get_queryset().filter(users=user)


class Organisation(models.Model):
    orgId = models.CharField(max_length=255, unique=True, default=custom_id)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(CustomUser, related_name="organisations")
    user_org = OrganizationManager()
    objects = models.Manager()

    def __str__(self):
        return self.name
