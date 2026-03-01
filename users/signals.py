from typing import Any
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, UserRole, PatientProfile


@receiver(post_save, sender=CustomUser)
@transaction.atomic
def create_user_profile(sender: type[CustomUser], instance: CustomUser, created: bool, **_kwargs: Any) -> None:
    """
    Automatically create the appropriate profile based on user's role.
    - PATIENT role -> PatientProfile
    - NURSE role -> Does not auto-create profile here (requires strict agency assignment elsewhere).

    Uses get_or_create to be idempotent:
    - Safe for new user creation
    - Safe for role changes on existing users
    - Won't overwrite existing profile data
    """
    if instance.role == UserRole.PATIENT:
        PatientProfile.objects.get_or_create(user=instance)
    
    elif instance.role == UserRole.NURSE:
        # A nurse must be created with an agency assigned initially, handled elsewhere, 
        # but the empty profile can be created here.
        pass

    elif instance.role == UserRole.AGENCY_ADMIN:
        # The ticket dictates: `if created and instance.role == 'AGENCY_ADMIN':` -> automatically create an empty `AgencyProfile` 
        # linked to this user.
        if created and not instance.agency:
            from .models import AgencyProfile
            agency = AgencyProfile.objects.create(
                manager_name=instance.get_full_name() or "New Agency Manager",
                commercial_registry=f"PENDING-{instance.id}", # Placeholder to satisfy unique constraint
                moh_license_number=f"PENDING-{instance.id}",
                tax_id=f"PENDING-{instance.id}"
            )
            instance.agency = agency
            instance.save(update_fields=['agency'])
