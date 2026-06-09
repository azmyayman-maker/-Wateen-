"""
KYC Service Layer — OpenCV + Tesseract OCR for Egyptian National ID Extraction.

This module handles:
1. Image preprocessing (grayscale, thresholding, noise reduction)
2. OCR text extraction (Arabic + English via Tesseract)
3. National ID regex extraction (14-digit Egyptian format)
4. Verification logic (compare extracted vs. registered ID)

SECURITY: This module NEVER logs raw National ID images or extracted text.
"""

import logging
import re
from typing import Optional

import cv2
import numpy as np
import pytesseract
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from PIL import Image

logger = logging.getLogger(__name__)

# Regex for Egyptian National ID: starts with 2 or 3, followed by 13 digits
NATIONAL_ID_PATTERN = re.compile(r'[23]\d{13}')


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Apply OpenCV preprocessing to improve OCR accuracy.

    Pipeline:
        1. Decode raw bytes → OpenCV image
        2. Convert to grayscale
        3. Apply bilateral filter (preserves edges while removing noise)
        4. Apply adaptive thresholding (handles uneven lighting)
        5. Apply morphological closing (fill small gaps in text)

    Args:
        image_bytes: Raw image file bytes.

    Returns:
        Preprocessed image as numpy array (grayscale, thresholded).

    Raises:
        ValueError: If image cannot be decoded.
    """
    # Decode image from bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Could not decode image. Ensure the file is a valid image.")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Bilateral filter: reduces noise while keeping edges sharp
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)

    # Adaptive thresholding: handles shadows and uneven lighting on ID cards
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11,
        C=2,
    )

    # Morphological closing to fill small gaps in characters
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    return closed


def extract_national_id(uploaded_file: UploadedFile) -> tuple[Optional[str], str]:
    """
    Extract the 14-digit Egyptian National ID from an uploaded document image.

    Steps:
        1. Read and preprocess the image with OpenCV
        2. Run Tesseract OCR with Arabic + English language support
        3. Search for 14-digit National ID pattern via regex

    Args:
        uploaded_file: Django UploadedFile from the request.

    Returns:
        Tuple of (extracted_national_id, raw_ocr_text).
        extracted_national_id is None if no valid 14-digit ID found.

    Note:
        This function intentionally does NOT log the raw OCR text
        or extracted ID for security reasons.
    """
    try:
        # Read file bytes (handles both InMemoryUploadedFile and TemporaryUploadedFile)
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset for potential re-use

        # Preprocess with OpenCV
        processed_image = preprocess_image(image_bytes)

        # Convert OpenCV image to PIL Image for pytesseract
        pil_image = Image.fromarray(processed_image)

        # Run Tesseract OCR with both Arabic and English
        # Arabic for name fields, English for the numeric National ID
        raw_text = pytesseract.image_to_string(
            pil_image,
            lang='ara+eng',
            config='--psm 6',  # Assume uniform block of text
        )

        # Also run with digits-only mode for better number extraction
        digits_text = pytesseract.image_to_string(
            pil_image,
            lang='eng',
            config='--psm 6 -c tessedit_char_whitelist=0123456789',
        )

        # Combine both OCR outputs for maximum extraction coverage
        combined_text = f"{raw_text}\n{digits_text}"

        # Find all 14-digit sequences matching Egyptian National ID format
        matches = NATIONAL_ID_PATTERN.findall(combined_text)

        if matches:
            # Return the first valid match
            extracted_id = matches[0]
            logger.info("KYC: National ID pattern found in document.")
            return extracted_id, raw_text

        logger.info("KYC: No National ID pattern found in document.")
        return None, raw_text

    except ValueError as e:
        logger.warning("KYC: Image preprocessing failed: %s", str(e))
        return None, ""
    except pytesseract.TesseractError as e:
        logger.warning("KYC: Tesseract OCR failed: %s", str(e))
        return None, ""
    except Exception as e:
        # Catch-all: never crash the caller
        logger.error("KYC: Unexpected error during OCR: %s", type(e).__name__)
        return None, ""


def verify_kyc_document(nurse_document, expected_national_id: str) -> dict:
    """
    Verify a KYC document by extracting the National ID and comparing it
    against the nurse's registered ID.

    Args:
        nurse_document: NurseDocument model instance (with document_file attached).
        expected_national_id: The 14-digit National ID from the user's registration.

    Returns:
        Dict with keys: status ('verified'|'rejected'), reason (str), extracted_id (str|None).

    Side effects:
        - Updates nurse_document.status, .ocr_data, .extracted_national_id, .verified_at
        - Updates NurseProfile.verification_status if all documents are verified
    """
    from users.models import DocumentStatus

    extracted_id, raw_text = extract_national_id(nurse_document.document_file)

    # Store OCR metadata (NOT the raw image or full text — only safe metadata)
    nurse_document.ocr_data = {
        'ocr_completed': True,
        'id_found': extracted_id is not None,
        'text_length': len(raw_text),
        'processed_at': timezone.now().isoformat(),
    }

    if extracted_id is None:
        nurse_document.status = DocumentStatus.REJECTED
        nurse_document.rejection_reason = (
            'تعذّر قراءة الرقم القومي من الصورة. '
            'يرجى رفع صورة واضحة عالية الجودة.'
        )
        nurse_document.save()

        logger.info("KYC: Document rejected — no ID extracted.")
        return {
            'status': 'rejected',
            'reason': (
                'Could not read National ID clearly. '
                'Please upload a high-quality image.'
            ),
            'extracted_id': None,
        }

    nurse_document.extracted_national_id = extracted_id

    # Compare extracted ID with the user's registered National ID
    if extracted_id == expected_national_id:
        nurse_document.status = DocumentStatus.VERIFIED
        nurse_document.rejection_reason = ''
        nurse_document.verified_at = timezone.now()
        nurse_document.save()

        # Check if ALL required documents are now verified
        _check_full_verification(nurse_document.nurse)

        logger.info("KYC: Document verified successfully.")
        return {
            'status': 'verified',
            'reason': 'National ID verified successfully.',
            'extracted_id': extracted_id,
        }
    else:
        nurse_document.status = DocumentStatus.REJECTED
        nurse_document.rejection_reason = (
            'الرقم القومي المستخرج لا يتطابق مع الرقم المسجّل.'
        )
        nurse_document.save()

        logger.info("KYC: Document rejected — ID mismatch.")
        return {
            'status': 'rejected',
            'reason': (
                'Extracted National ID does not match the registered ID. '
                'Please upload the correct document.'
            ),
            'extracted_id': None,  # Do not expose the extracted ID on mismatch
        }


def _check_full_verification(nurse_profile) -> None:
    """
    If ALL required document types are verified, update the NurseProfile
    verification_status to VERIFIED.
    """
    from users.models import DocumentStatus, DocumentType, VerificationStatus

    required_types = {DocumentType.NATIONAL_ID, DocumentType.SYNDICATE_CARD}

    verified_types = set(
        nurse_profile.documents
        .filter(status=DocumentStatus.VERIFIED)
        .values_list('document_type', flat=True)
    )

    if required_types.issubset(verified_types):
        nurse_profile.verification_status = VerificationStatus.VERIFIED
        nurse_profile.save(update_fields=['verification_status'])
        logger.info("KYC: Nurse fully verified — all documents passed.")
