import magic
import re
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


EGYPTIAN_NATIONAL_ID_REGEX = re.compile(r'^[23]\d{13}$')

GOVERNORATE_CODES = {
    '01', '02', '03', '04', '11', '12', '13', '14', '15', '16',
    '17', '18', '19', '21', '22', '23', '24', '25', '26', '27',
    '28', '29', '31', '32', '33', '34', '35'
}


def validate_egyptian_national_id(value: str) -> None:
    if not value:
        raise ValidationError(
            _('الرقم القومي مطلوب'),
            code='required'
        )
    
    if not isinstance(value, str):
        raise ValidationError(
            _('الرقم القومي يجب أن يكون نصاً'),
            code='invalid_type'
        )
    
    if len(value) != 14:
        raise ValidationError(
            _('الرقم القومي يجب أن يتكون من 14 رقم'),
            code='invalid_length'
        )
    
    if not value.isdigit():
        raise ValidationError(
            _('الرقم القومي يجب أن يحتوي على أرقام فقط'),
            code='non_numeric'
        )
    
    century_digit = value[0]
    if century_digit not in ('2', '3'):
        raise ValidationError(
            _('الرقم القومي يجب أن يبدأ بـ 2 أو 3'),
            code='invalid_century'
        )
    
    birth_year = value[1:3]
    birth_month = value[3:5]
    birth_day = value[5:7]
    
    try:
        month_int = int(birth_month)
        day_int = int(birth_day)
        year_int = int(birth_year)
        
        if month_int < 1 or month_int > 12:
            raise ValidationError(
                _('شهر الميلاد في الرقم القومي غير صحيح'),
                code='invalid_month'
            )
        
        if day_int < 1 or day_int > 31:
            raise ValidationError(
                _('يوم الميلاد في الرقم القومي غير صحيح'),
                code='invalid_day'
            )
        
        # Calculate full 4-digit year for accurate leap year check
        full_year = (1900 if century_digit == '2' else 2000) + year_int
        is_leap_year = (full_year % 4 == 0 and (full_year % 100 != 0 or full_year % 400 == 0))
        
        days_per_month = [31, 29 if is_leap_year else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if day_int > days_per_month[month_int - 1]:
            raise ValidationError(
                _('يوم الميلاد في الرقم القومي غير صحيح'),
                code='invalid_day_for_month'
            )
        
    except ValueError:
        raise ValidationError(
            _('تاريخ الميلاد في الرقم القومي غير صحيح'),
            code='invalid_date'
        )
    
    governorate_code = value[7:9]
    if governorate_code not in GOVERNORATE_CODES:
        raise ValidationError(
            _('كود المحافظة في الرقم القومي غير صحيح'),
            code='invalid_governorate'
        )


def validate_phone_number(value: str) -> None:
    if not value:
        raise ValidationError(
            _('رقم الهاتف مطلوب'),
            code='required'
        )
    
    if not isinstance(value, str):
        raise ValidationError(
            _('رقم الهاتف يجب أن يكون نصاً'),
            code='invalid_type'
        )
    
    phone_pattern = re.compile(r'^01[0125]\d{8}$')
    if not phone_pattern.match(value):
        raise ValidationError(
            _('رقم الهاتف يجب أن يكون 11 رقم ويبدأ بـ 01'),
            code='invalid_phone'
        )


def validate_kyc_file_extension_and_size(file: UploadedFile) -> None:
    """
    Validate that the uploaded file is a PDF or Image and under 10MB.
    Uses python-magic for secure MIME-type sniffing (Law 151/2020 Compliance).
    """
    # 1. Size check (10MB limit)
    MAX_SIZE = 10 * 1024 * 1024
    if file.size > MAX_SIZE:
        raise ValidationError(
            _("حجم الملف يتجاوز الحد المسموح به (10 ميجابايت)."),
            code='file_too_large'
        )

    # 2. Content check (MIME-type sniffing)
    # Read first 2048 bytes for sniffing
    initial_bytes = file.read(2048)
    file.seek(0)  # Reset pointer for subsequent reads/saves
    
    mime_type = magic.from_buffer(initial_bytes, mime=True)
    allowed_mimes = ["application/pdf", "image/jpeg", "image/png"]
    
    if mime_type not in allowed_mimes:
        raise ValidationError(
            _("نوع الملف غير مسموح. المسموح فقط: PDF, JPEG, PNG."),
            code='invalid_file_type'
        )
    
    return file