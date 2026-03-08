# Ticket 4.2 — KYC Workflow (OCR National ID Verification) — Report

**Date:** 2026-02-22  
**Status:** ✅ Implementation Complete — Pending Migration & Docker Rebuild  
**Phase:** 4 — Trust & Verification  
**MIP Reference:** Section 3.4 — AI-Enhanced Trust System — Advanced KYC Workflow

---

## Overview

Built a complete KYC (Know Your Customer) workflow for Nurse registration in the Wateen Healthcare Platform. The system accepts uploads of the Egyptian National ID and Nursing Syndicate Card, processes images through an OpenCV preprocessing pipeline + Tesseract OCR, extracts the 14-digit National ID number, and validates it against the nurse's registered ID.

---

## Deliverables

### 1. Environment Setup

**Dockerfile additions** (`docker/Dockerfile`):

- `tesseract-ocr` — OCR engine
- `tesseract-ocr-ara` — Arabic language data
- `libgl1-mesa-glx` — OpenCV dependency

**Python packages** (`requirements/base.txt`):

- `opencv-python-headless==4.9.0.80`
- `pytesseract==0.3.10`
- `Pillow==10.2.0`

### 2. NurseDocument Model

New model in `users/models.py` with:

- `DocumentType` enum: `NATIONAL_ID`, `SYNDICATE_CARD`
- `DocumentStatus` enum: `PENDING`, `VERIFIED`, `REJECTED`
- UUID primary key, FK to NurseProfile, FileField, JSONField for OCR data
- Unique constraint: one document per type per nurse

### 3. KYC Service Layer

`users/services/kyc_service.py` — isolated service with 3 core functions:

| Function                | Purpose                                                            |
| ----------------------- | ------------------------------------------------------------------ |
| `preprocess_image()`    | Bilateral filter → Adaptive threshold → Morphological closing      |
| `extract_national_id()` | Dual-pass Tesseract OCR (ara+eng & digits-only) + regex matching   |
| `verify_kyc_document()` | Compare extracted vs registered ID, update document/profile status |

### 4. API Endpoint

`POST /api/v1/kyc/upload/` — `multipart/form-data`

| Input           | Type   | Description                           |
| --------------- | ------ | ------------------------------------- |
| `document_type` | string | `NATIONAL_ID` or `SYNDICATE_CARD`     |
| `document_file` | file   | Image (JPEG/PNG/BMP/TIFF/WebP, ≤10MB) |

Returns `200 OK` with `status: "verified"` or `status: "rejected"` — **never a 500 error**.

### 5. Security Measures

- ✅ `opencv-python-headless` (no GUI — safe for Docker)
- ✅ Raw National ID text **never** logged
- ✅ OCR metadata stored, not raw image text
- ✅ File size cap (10MB)
- ✅ File type validation (image formats only)

### 6. Test Coverage

| Test Class               | Methods | Scope                               |
| ------------------------ | ------- | ----------------------------------- |
| `TestNurseDocumentModel` | 6       | Model CRUD, uniqueness, cascade     |
| `TestKYCService`         | 3       | Regex, preprocessing, OCR function  |
| `TestKYCUploadAPI`       | 7       | Auth, role, validation, upload flow |

---

## Files Modified/Created

| File                            | Status   |
| ------------------------------- | -------- |
| `docker/Dockerfile`             | Modified |
| `requirements/base.txt`         | Modified |
| `config/settings.py`            | Modified |
| `users/models.py`               | Modified |
| `users/services/__init__.py`    | **New**  |
| `users/services/kyc_service.py` | **New**  |
| `users/serializers.py`          | Modified |
| `users/views.py`                | Modified |
| `users/urls.py`                 | Modified |
| `users/admin.py`                | Modified |
| `users/tests.py`                | Modified |

---

## Pending Actions (Human Lead)

1. `python manage.py makemigrations users`
2. `docker compose -f docker/docker-compose.yml build --no-cache`
3. `docker compose exec web python manage.py migrate`
4. `docker compose exec web python manage.py test users -v2`
5. Manual Postman test with a real Egyptian National ID photo
