---
ticket: "1.4-QA"
title: "QA Protocol: Profiles Architecture Verification"
role: "Kilo (Quality Assurance)"
priority: critical
depends_on: "1.4 (Profiles Implemented)"
---

# Quality Assurance Protocol: Profiles Architecture

**Objective:** Verify the structural integrity, database consistency, and functional correctness of the Patient and Nurse profile implementation.

## 1. Database Integrity Verification

Ensure the database schema correctly reflects the new models.

### 1.1. Check Migrations Status

Run inside the Docker container:

```bash
python manage.py showmigrations users
```

**Expected Output:**

- `[X] 0001_initial`
- `[ ] 0002_nurseprofile_patientprofile` (if not applied yet)

### 1.2. Apply Schema Changes

Execute the migration to sync the database:

```bash
python manage.py migrate users
```

**Success Criteria:** Application of `0002_nurseprofile_patientprofile` completes without errors.

---

## 2. Automated Testing Suite

Execute the test suite to validate logic and signals.

### 2.1. Run Unit Tests

```bash
python manage.py test users -v 2
```

**Focus Areas:**

- `TestPatientProfileSignal`: Verifies auto-creation of PatientProfile.
- `TestNurseProfileSignal`: Verifies auto-creation of NurseProfile.
- `TestProfileModelStr`: Verifies string representation.

**Success Criteria:** All tests passed (OK). Zero failures/errors.

---

## 3. Functional Verification (Interactive Shell)

Manually verify the `post_save` signal logic using the Django shell.

Open the shell:

```bash
python manage.py shell
```

### 3.1. Verify Patient Profile Creation

```python
from django.contrib.auth import get_user_model
from users.models import UserRole, PatientProfile

User = get_user_model()

# Create a Patient
patient = User.objects.create_user(
    national_id='30001011234567',
    phone_number='01099998888',
    password='TestPass123!',
    role=UserRole.PATIENT
)

# Verify Profile Exists
profile = PatientProfile.objects.get(user=patient)
print(f"Patient Profile Created: {profile}")
# Expected: PatientProfile(30001011234567)
```

### 3.2. Verify Nurse Profile Creation

```python
from users.models import NurseProfile

# Create a Nurse
nurse = User.objects.create_user(
    national_id='30001011234568',
    phone_number='01099997777',
    password='TestPass123!',
    role=UserRole.NURSE
)

# Verify Profile Exists
profile = NurseProfile.objects.get(user=nurse)
print(f"Nurse Profile Created: {profile}")
# Expected: NurseProfile(30001011234568)
```

---

## 4. Admin Panel Verification

1.  **Login** to the Django Admin (`/admin`).
2.  Navigate to **Users** app.
3.  **Patient Profiles / ملفات المرضى**: Ensure the table is visible and populated.
4.  **Nurse Profiles / ملفات الممرضين**: Ensure the table is visible and populated.
5.  **Verify Data**: Click on a profile to ensure details (like `gender`, `wearables_enabled`, `rating`) are editable.

---

## 5. Final Sign-off

- [ ] Database Migrations Applied
- [ ] Automated Tests Passed
- [ ] Manual Shell Verification Successful
- [ ] Admin Panel Verified
