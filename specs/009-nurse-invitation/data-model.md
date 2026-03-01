# Data Model: Nurse Invitation Flow

## Entities

### `NurseProfile` (Update)

Represents a MoH-Licensed nurse securely bound to an agency. Modifying existing schema to enforce strict relation.

**Fields**:

- `user`: `OneToOneField(CustomUser, on_delete=CASCADE, primary_key=True)`
- `agency`: `ForeignKey(AgencyProfile, null=False, blank=False, on_delete=CASCADE)` - **Constraint Enforced**
- `full_name`: `CharField(max_length=255)`
- `national_id`: `CharField(max_length=14, unique=True)`
- `syndicate_id`: `CharField(max_length=50, unique=True)`
- `is_available`: `BooleanField(default=False)`
- `last_location`: `PointField(srid=4326, null=True, blank=True)`

**Indexes**:

- `GistIndex` on `last_location`.

### `NurseInvitation` (New)

Represents a cryptographic invitation issued by an Agency Admin to a prospective nurse.

**Fields**:

- `id`: `UUIDField(primary_key=True)`
- `agency`: `ForeignKey(AgencyProfile, on_delete=CASCADE)`
- `phone`: `CharField(max_length=20)`
- `token`: `UUIDField(unique=True, db_index=True)`
- `status`: `CharField(choices=[PENDING, ACCEPTED, EXPIRED], default=PENDING)`
- `expires_at`: `DateTimeField()`
- `created_at`: `DateTimeField(auto_now_add=True)`

**State Transitions**:

- `PENDING` -> `ACCEPTED` (upon successful registration)
- `PENDING` -> `EXPIRED` (cron job or time-based validation)
