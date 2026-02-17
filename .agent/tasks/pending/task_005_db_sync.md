---
ticket: "1.4-sync"
title: "Database Sync (Migrations)"
priority: high
depends_on: "1.4 (Profiles Architecture)"
estimated_complexity: low
---

# Database Sync

Execute database migrations to apply the changes from Ticket 1.4 (PatientProfile & NurseProfile).

## Instructions

Run the following commands strictly from the project root (the directory containing the `docker/` folder):

1. **Make Migrations for Users App:**

   ```bash
   docker-compose -f docker/docker-compose.yml exec web python manage.py makemigrations users
   ```

2. **Apply Migrations:**
   ```bash
   docker-compose -f docker/docker-compose.yml exec web python manage.py migrate
   ```

## Verification

Check the output of `migrate` to confirm `users` migrations were applied (e.g., `Applying users.0002_patientprofile_nurseprofile... OK`).
