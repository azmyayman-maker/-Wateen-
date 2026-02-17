from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, UserRole, PatientProfile, NurseProfile


@receiver(post_save, sender=CustomUser)
@transaction.atomic
def create_user_profile(_sender, instance, _created, **_kwargs):
    """
    Automatically create the appropriate profile based on user's role.
    - PATIENT role -> PatientProfile
    - NURSE role -> NurseProfile

    Uses get_or_create to be idempotent:
    - Safe for new user creation
    - Safe for role changes on existing users
    - Won't overwrite existing profile data
    """
    if instance.role == UserRole.PATIENT:
        PatientProfile.objects.get_or_create(user=instance)
    elif instance.role == UserRole.NURSE:
        NurseProfile.objects.get_or_create(user=instance)
