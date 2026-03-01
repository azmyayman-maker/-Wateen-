# Quickstart: Nurse Invitation Flow

## Setup

1. Ensure the PostgreSQL and Redis containers are running via Docker.
2. Run database migrations to apply the committed `NurseInvitation` model and update `NurseProfile`:
   `python manage.py migrate`

## Testing the Flow

1. Obtain an `access_token` for a user with the role `AGENCY_ADMIN`.
2. Invite a nurse:
   ```bash
   curl -X POST http://localhost:8000/api/v1/agencies/invite-nurse/ \
        -H "Authorization: Bearer <access_token>" \
        -H "Content-Type: application/json" \
        -d '{"phone": "01000000000"}'
   ```
3. Copy the `token` from the response.
4. Accept the invitation as the nurse:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/accept-invitation/ \
        -H "Content-Type: application/json" \
        -d '{"token": "<token_here>", "password": "PassWord1!", "email": "n@n.com", "national_id": "290", "syndicate_id": "SYN1", "full_name": "Test"}'
   ```
