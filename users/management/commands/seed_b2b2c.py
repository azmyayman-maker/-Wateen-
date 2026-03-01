from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import AgencyProfile, NurseProfile, AgencyStatus, DispatchMode

class Command(BaseCommand):
    help = 'Migrates legacy P2P nurses to the Wateen Internal Agency (B2B2C Migration)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting P2P to B2B2C data migration...'))
        
        with transaction.atomic():
            # Create or get the default Internal Agency
            internal_agency, created = AgencyProfile.objects.get_or_create(
                manager_name="Wateen Internal Administration",
                commercial_registry="WATEEN-INTERNAL-001",
                moh_license_number="WATEEN-MOH-001",
                tax_id="000-000-000",
                defaults={
                    'status': AgencyStatus.VERIFIED,
                    'rating': 5.0,
                    'dispatch_mode': DispatchMode.AUTO,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS('Created "Wateen Internal Agency".'))
            else:
                self.stdout.write(self.style.NOTICE('Internal Agency already exists.'))
            
            # Find all nurses without an agency
            orphan_nurses = NurseProfile.objects.filter(agency__isnull=True)
            count = orphan_nurses.count()
            
            if count == 0:
                self.stdout.write(self.style.SUCCESS('No orphaned nurses found. Migration complete.'))
                return
            
            self.stdout.write(self.style.NOTICE(f'Found {count} orphaned nurses. Assigning to Internal Agency...'))
            
            # Update all orphan nurses
            updated_count = orphan_nurses.update(agency=internal_agency)
            
            # Update agency network capacity
            internal_agency.network_capacity = NurseProfile.objects.filter(agency=internal_agency).count()
            internal_agency.save(update_fields=['network_capacity'])
            
            self.stdout.write(self.style.SUCCESS(f'Successfully migrated {updated_count} nurses and updated network capacity.'))
