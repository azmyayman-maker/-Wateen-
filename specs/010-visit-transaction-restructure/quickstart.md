# Quickstart: Visit & Transaction Model Restructuring

**Feature**: 010-visit-transaction-restructure  
**Date**: 2026-03-01

## Prerequisites

- Python 3.11+ with Django 5.2
- PostgreSQL 16 + PostGIS 3.4
- Virtual environment activated (`source .venv/bin/activate` or `.\venv\Scripts\activate`)

## Setup After Implementation

```bash
# 1. Generate migrations
python manage.py makemigrations visits

# 2. Apply migrations
python manage.py migrate

# 3. Verify models load correctly
python manage.py shell -c "from visits.models import Visit, Transaction, VisitStatus, TransactionStatus; print('Models OK')"

# 4. Run tests
pytest visits/tests/ -v

# 5. Verify admin registration
python manage.py shell -c "
from django.contrib import admin
from visits.models import Visit, Transaction
from users.models import AgencyProfile
print('Visit registered:', admin.site.is_registered(Visit))
print('Transaction registered:', admin.site.is_registered(Transaction))
print('AgencyProfile registered:', admin.site.is_registered(AgencyProfile))
"
```

## Key Verification Points

1. **State Machine**: Create a Visit and test `transition_to()` through all valid paths
2. **Immutability**: Modify `final_price` on a saved Visit → expect `ValidationError`
3. **Auto-calc**: Save a Transaction with `amount_paid=1000.00` → verify `agency_payout=850.00`
4. **Admin**: Log into admin → verify financial fields are read-only, AgencyProfile has map widget
