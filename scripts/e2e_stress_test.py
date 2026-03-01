import os
import django
import uuid
from decimal import Decimal
from django.contrib.gis.geos import Point

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser, AgencyProfile, PatientProfile, NurseProfile, AgencyStatus
from visits.models import Visit, VisitStatus, ServiceType, Transaction, TransactionStatus
from visits.services.dispatch import DispatchEngine
from visits.services.settlement import SettlementService

def run_simulation():
    print("🚀 Starting E2E Stress Test Simulation...")
    
    # 1. Setup Test Data
    print("--- 1. Setting up Test Data ---")
    patient_user, _ = CustomUser.objects.get_or_create(username="sim_patient", role="PATIENT")
    patient, _ = PatientProfile.objects.get_or_create(user=patient_user)
    
    agency_user, _ = CustomUser.objects.get_or_create(username="sim_agency", role="AGENCY")
    agency, _ = AgencyProfile.objects.get_or_create(
        user=agency_user, 
        manager_name="Simulation Agency",
        status=AgencyStatus.VERIFIED,
        stripe_account_id="acct_sim_123"
    )
    
    nurse_user, _ = CustomUser.objects.get_or_create(username="sim_nurse", role="NURSE")
    nurse, _ = NurseProfile.objects.get_or_create(user=nurse_user, agency=agency, is_available=True)
    
    service, _ = ServiceType.objects.get_or_create(name="E2E Test Service", base_price=100.00)
    
    # 2. Patient Request
    print("--- 2. Patient Requesting Visit ---")
    location = Point(31.2357, 30.0444) # Cairo
    visit = Visit.objects.create(
        patient=patient,
        agency=agency,
        service_type=service,
        location=location,
        status=VisitStatus.PENDING_AGENCY,
        final_price=service.base_price
    )
    print(f"Created Visit: {visit.id}")
    
    # Initialize Transaction
    transaction = SettlementService.create_transaction_for_visit(visit)
    print(f"Initialized Transaction: {transaction.id} | Split: Wateen={transaction.take_rate_amount}, Agency={transaction.agency_amount}")
    
    # 3. Agency Dispatch
    print("--- 3. Agency Manual Dispatching to Nurse ---")
    visit.nurse = nurse
    visit.transition_to(VisitStatus.PENDING_NURSE)
    print(f"Visit assigned to Nurse: {nurse.user.username}")
    
    # 4. Nurse Acceptance
    print("--- 4. Nurse Accepting Visit ---")
    visit.transition_to(VisitStatus.ACCEPTED)
    print("Visit Accepted.")
    
    # 5. Visit Completion
    print("--- 5. Visit Completion ---")
    visit.transition_to(VisitStatus.EN_ROUTE)
    visit.transition_to(VisitStatus.IN_PROGRESS)
    visit.transition_to(VisitStatus.COMPLETED)
    print("Visit marked as COMPLETED.")
    
    # 6. Settle Transaction
    print("--- 6. Running Settlement Task ---")
    # Simulate escrow first
    transaction.status = TransactionStatus.ESCROWED
    transaction.save()
    
    SettlementService.settle_visit(visit)
    transaction.refresh_from_db()
    agency.refresh_from_db()
    
    print(f"Transaction Status: {transaction.status}")
    print(f"Agency Wallet Balance: {agency.wallet_balance} EGP")
    
    print("✅ Simulation Finished Successfully!")

if __name__ == "__main__":
    run_simulation()
