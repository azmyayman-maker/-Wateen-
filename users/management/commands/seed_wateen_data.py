"""
Wateen Zero-Trace Seeder — seed_wateen_data
=============================================
Django management command that generates massive, realistic test data
for the Wateen B2B2C Healthcare platform.

ZERO-TRACE PATTERN: All entities are isolated via @wateen-test-seed.local
email domain and TEST-prefixed b2b identifiers. Every generated row
is 100% removable via the companion `nuke_test_data` command.

Usage:
    python manage.py seed_wateen_data
    python manage.py seed_wateen_data --agencies 50 --nurses-per-agency 20 --visits-per-nurse 50
    python manage.py seed_wateen_data --agencies 100 --batch-size 1000
"""

import random
import time
import uuid
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from users.models import (
    AgencyProfile,
    AgencyStatus,
    CustomUser,
    DispatchMode,
    NurseProfile,
    PatientProfile,
    UserRole,
    VerificationStatus,
)
from users.utils.seed_helpers import (
    CAIRO_DISTRICTS,
    TEST_EMAIL_DOMAIN,
    generate_arabic_name,
    generate_cairo_polygon,
    generate_commercial_registry,
    generate_egyptian_phone,
    generate_moh_license,
    generate_point_inside_polygon,
    generate_pricing_snapshot,
    generate_random_visit_status,
    generate_tax_id,
    generate_test_email,
    generate_valid_national_id,
    NURSE_SPECIALIZATIONS,
)
from visits.models import (
    ServiceType,
    Transaction,
    TransactionStatus,
    Visit,
    VisitStatus,
)


class Command(BaseCommand):
    help = (
        "Generate massive, realistic test data for Wateen B2B2C stress testing. "
        "All data is isolated via @wateen-test-seed.local and removable with nuke_test_data."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--agencies",
            type=int,
            default=50,
            help="Number of test agencies to create (default: 50)",
        )
        parser.add_argument(
            "--nurses-per-agency",
            type=int,
            default=20,
            help="Number of nurses per agency (default: 20)",
        )
        parser.add_argument(
            "--visits-per-nurse",
            type=int,
            default=50,
            help="Number of visits per nurse (default: 50)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="bulk_create batch size for memory control (default: 500)",
        )

    def handle(self, *args, **options):
        num_agencies = options["agencies"]
        nurses_per_agency = options["nurses_per_agency"]
        visits_per_nurse = options["visits_per_nurse"]
        batch_size = options["batch_size"]

        total_nurses = num_agencies * nurses_per_agency
        total_patients = num_agencies * nurses_per_agency  # 1 patient per nurse
        total_visits = total_nurses * visits_per_nurse
        total_entities = num_agencies + total_nurses + total_patients + total_visits

        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.NOTICE("  WATEEN ZERO-TRACE SEEDER"))
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(f"  Agencies:           {num_agencies:,}")
        self.stdout.write(f"  Nurses/Agency:      {nurses_per_agency:,}")
        self.stdout.write(f"  Visits/Nurse:       {visits_per_nurse:,}")
        self.stdout.write(f"  Batch Size:         {batch_size:,}")
        self.stdout.write(self.style.NOTICE("-" * 70))
        self.stdout.write(f"  Total Users:        {(num_agencies + total_nurses + total_patients):,}")
        self.stdout.write(f"  Total Visits:       {total_visits:,}")
        self.stdout.write(f"  Estimated Rows:     ~{total_entities:,}")
        self.stdout.write(f"  Isolation Domain:   @{TEST_EMAIL_DOMAIN}")
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write("")

        start_time = time.time()

        # ── Step 0: Ensure ServiceTypes exist ────────────────────────────
        service_types = self._ensure_service_types()
        self.stdout.write(self.style.SUCCESS(
            f"  [✓] Service Types:  {len(service_types)} available"
        ))

        # ── Step 1: Determine starting index to avoid collisions ─────────
        existing_test_agencies = AgencyProfile.objects.filter(
            commercial_registry__startswith="TEST-CR-"
        ).count()
        start_index = existing_test_agencies

        districts = list(CAIRO_DISTRICTS.keys())

        # ── Step 2: Generate per-agency batches ──────────────────────────
        for agency_idx in range(start_index, start_index + num_agencies):
            self._seed_agency_batch(
                agency_idx=agency_idx,
                nurses_per_agency=nurses_per_agency,
                visits_per_nurse=visits_per_nurse,
                batch_size=batch_size,
                districts=districts,
                service_types=service_types,
            )

            # Progress reporting
            done = agency_idx - start_index + 1
            pct = (done / num_agencies) * 100
            elapsed = time.time() - start_time
            self.stdout.write(
                f"  [{done:>4}/{num_agencies}] "
                f"Agency {agency_idx:>4} seeded "
                f"({pct:5.1f}%, {elapsed:.1f}s elapsed)"
            )

        # ── Final Summary ────────────────────────────────────────────────
        elapsed = time.time() - start_time
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("  SEEDING COMPLETE"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(f"  Duration:           {elapsed:.2f}s")
        self.stdout.write(f"  Agencies Created:   {num_agencies:,}")
        self.stdout.write(f"  Nurses Created:     {total_nurses:,}")
        self.stdout.write(f"  Patients Created:   {total_patients:,}")
        self.stdout.write(f"  Visits Created:     ~{total_visits:,}")
        self.stdout.write(self.style.SUCCESS("=" * 70))

    def _ensure_service_types(self) -> list:
        """Ensure test service types exist, create if necessary."""
        test_services = [
            ("تمريض منزلي", Decimal("200.00"), "خدمة تمريض منزلي شاملة"),
            ("علاج طبيعي", Decimal("300.00"), "جلسة علاج طبيعي"),
            ("رعاية كبار السن", Decimal("250.00"), "رعاية متخصصة لكبار السن"),
            ("عناية بالجروح", Decimal("180.00"), "تنظيف وتضميد الجروح"),
            ("حقن وريدي", Decimal("150.00"), "إعطاء محاليل وريدية"),
        ]
        service_type_objs = []
        for name, price, desc in test_services:
            obj, _ = ServiceType.objects.get_or_create(
                name=name,
                defaults={
                    "base_price": price,
                    "description": desc,
                    "is_active": True,
                },
            )
            service_type_objs.append(obj)
        return service_type_objs

    @transaction.atomic
    def _seed_agency_batch(
        self,
        agency_idx: int,
        nurses_per_agency: int,
        visits_per_nurse: int,
        batch_size: int,
        districts: list[str],
        service_types: list,
    ) -> None:
        """
        Seed a single agency with all its dependent entities inside
        a single atomic transaction for data integrity.
        """
        district = districts[agency_idx % len(districts)]
        polygon = generate_cairo_polygon(district)

        # ── 1. Create AgencyProfile ──────────────────────────────────────
        agency = AgencyProfile.objects.create(
            manager_name=f"{generate_arabic_name()[0]} {generate_arabic_name()[1]}",
            commercial_registry=generate_commercial_registry(agency_idx),
            moh_license_number=generate_moh_license(agency_idx),
            tax_id=generate_tax_id(agency_idx),
            status=AgencyStatus.VERIFIED,
            coverage_polygon=polygon,
            rating=round(random.uniform(3.5, 5.0), 1),
            network_capacity=nurses_per_agency,
            dispatch_mode=random.choice([DispatchMode.AUTO, DispatchMode.MANUAL]),
            wallet_balance=Decimal(str(random.randint(5000, 50000))),
        )

        # ── 2. Create Agency Admin User ──────────────────────────────────
        admin_first, admin_last = generate_arabic_name()
        # Use bulk_create to bypass signals (no auto-profile creation)
        admin_user = CustomUser(
            id=uuid.uuid4(),
            national_id=generate_valid_national_id(),
            phone_number=generate_egyptian_phone(),
            email=generate_test_email(f"agency-admin-{agency_idx}"),
            role=UserRole.AGENCY_ADMIN,
            first_name_ar=admin_first,
            last_name_ar=admin_last,
            is_active=True,
            agency=agency,
        )
        admin_user.set_unusable_password()
        # Direct save with signals disconnected via update_fields trick:
        # We save fields explicitly to avoid signal-triggered profile creation.
        CustomUser.objects.bulk_create([admin_user])

        # ── 3. Create Nurse Users (bulk) ─────────────────────────────────
        nurse_users = []
        for j in range(nurses_per_agency):
            first, last = generate_arabic_name()
            user = CustomUser(
                id=uuid.uuid4(),
                national_id=generate_valid_national_id(),
                phone_number=generate_egyptian_phone(),
                email=generate_test_email(f"nurse-{agency_idx}-{j}"),
                role=UserRole.NURSE,
                first_name_ar=first,
                last_name_ar=last,
                is_active=True,
                agency=agency,
            )
            user.set_unusable_password()
            nurse_users.append(user)

        CustomUser.objects.bulk_create(nurse_users, batch_size=batch_size)

        # ── 4. Create NurseProfiles (bulk) ───────────────────────────────
        nurse_profiles = []
        for j, user in enumerate(nurse_users):
            nurse_location = generate_point_inside_polygon(polygon)
            nurse_profiles.append(
                NurseProfile(
                    user=user,
                    agency=agency,
                    syndicate_number=f"TEST-SYN-{agency_idx:04d}-{j:04d}",
                    specializations=random.choice(NURSE_SPECIALIZATIONS),
                    rating=Decimal(str(round(random.uniform(3.0, 5.0), 2))),
                    is_available=random.choice([True, False]),
                    last_location=nurse_location,
                    verification_status=VerificationStatus.VERIFIED,
                )
            )
        NurseProfile.objects.bulk_create(nurse_profiles, batch_size=batch_size)

        # ── 5. Create Patient Users + Profiles (bulk) ────────────────────
        patient_users = []
        for j in range(nurses_per_agency):
            first, last = generate_arabic_name()
            patient = CustomUser(
                id=uuid.uuid4(),
                national_id=generate_valid_national_id(),
                phone_number=generate_egyptian_phone(),
                email=generate_test_email(f"patient-{agency_idx}-{j}"),
                role=UserRole.PATIENT,
                first_name_ar=first,
                last_name_ar=last,
                is_active=True,
            )
            patient.set_unusable_password()
            patient_users.append(patient)

        CustomUser.objects.bulk_create(patient_users, batch_size=batch_size)

        patient_profiles = []
        for patient_user in patient_users:
            home_loc = generate_point_inside_polygon(polygon)
            patient_profiles.append(
                PatientProfile(
                    user=patient_user,
                    home_location=home_loc,
                    gender=random.choice(["MALE", "FEMALE"]),
                    address_text=f"شارع {random.randint(1, 100)}، {district}، القاهرة",
                )
            )
        PatientProfile.objects.bulk_create(patient_profiles, batch_size=batch_size)

        # ── 6. Create Visits (bulk) ──────────────────────────────────────
        visits_to_create = []
        visit_objs_for_txn = []  # Track completed visits for transactions

        for j, nurse_profile in enumerate(nurse_profiles):
            patient_profile = patient_profiles[j % len(patient_profiles)]
            for v in range(visits_per_nurse):
                visit_id = uuid.uuid4()
                visit_status = generate_random_visit_status()
                pricing = generate_pricing_snapshot()
                visit_location = generate_point_inside_polygon(polygon)
                service_type = random.choice(service_types)

                visit = Visit(
                    id=visit_id,
                    patient=patient_profile,
                    agency=agency,
                    nurse=nurse_profile,
                    status=visit_status,
                    location=visit_location,
                    service_type=service_type,
                    base_price=pricing["base_price"],
                    distance_fee=pricing["distance_fee"],
                    distance_km=pricing["distance_km"],
                    distance_rate=pricing["distance_rate"],
                    time_multiplier=pricing["time_multiplier"],
                    ai_surge_coefficient=pricing["ai_surge_coefficient"],
                    final_price=pricing["final_price"],
                )
                visits_to_create.append(visit)

                # Only completed visits get transactions
                if visit_status == VisitStatus.COMPLETED:
                    visit_objs_for_txn.append((visit, pricing))

        Visit.objects.bulk_create(visits_to_create, batch_size=batch_size)

        # ── 7. Create Transactions for Completed Visits (bulk) ───────────
        transactions = []
        for visit, pricing in visit_objs_for_txn:
            take_rate = Decimal("15.00")
            amount = pricing["final_price"]
            payout = (amount * (Decimal("1") - take_rate / Decimal("100"))).quantize(
                Decimal("0.01")
            )
            txn_status = random.choice(
                [TransactionStatus.ESCROWED, TransactionStatus.SETTLED]
            )
            transactions.append(
                Transaction(
                    id=uuid.uuid4(),
                    visit=visit,
                    agency=agency,
                    amount_paid=amount,
                    wateen_take_rate=take_rate,
                    agency_payout=payout,
                    status=txn_status,
                    settled_at=timezone.now() if txn_status == TransactionStatus.SETTLED else None,
                )
            )

        if transactions:
            Transaction.objects.bulk_create(transactions, batch_size=batch_size)
