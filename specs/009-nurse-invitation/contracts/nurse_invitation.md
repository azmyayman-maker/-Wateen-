# Contracts: Nurse Invitation API

## Endpoints

### 1. Invite Nurse

**URL**: `POST /api/v1/agency/invite-nurse/`
**Auth**: `IsAuthenticated`, `IsAgencyAdmin`

**Request Payload**:

```json
{
  "phone": "01012345678"
}
```

**Response Payload (201 Created)**:

```json
{
  "token": "db200d5f-fc14-43cb-bae3-1cbacfbcdef1",
  "expires_at": "2026-03-04T12:00:00Z"
}
```

### 2. Accept Invitation

**URL**: `POST /api/v1/auth/accept-invitation/`
**Auth**: `AllowAny`

**Request Payload**:

```json
{
  "token": "db200d5f-fc14-43cb-bae3-1cbacfbcdef1",
  "password": "SecurePassword123",
  "email": "nurse@example.com",
  "national_id": "29001011234567",
  "syndicate_number": "SYN-12345",
  "full_name": "Fatima Ahmed"
}
```

**Response Payload (201 Created)**:

```json
{
  "message": "Nurse registration successful",
  "user_id": "f5f7f8f9...",
  "agency_id": "a2a3a4..."
}
```

**Error Parameters**:

- **400 Bad Request**: Invalid or missing fields.
  ```json
  {
    "detail": "token, password, national_id, syndicate_number and phone are required."
  }
  ```
- **404 Not Found**: Unknown token.
  ```json
  {
    "detail": "Invalid or already consumed invitation token."
  }
  ```
- **410 Gone**: Expired or consumed token.
  ```json
  {
    "detail": "Invitation has expired."
  }
  ```
