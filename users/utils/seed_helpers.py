"""
Wateen Zero-Trace Seeding Utilities
====================================
Egyptian data generators and Greater Cairo PostGIS helpers for realistic
mock data generation. All generators produce data that passes the project's
strict validators (national_id, phone_number).

ISOLATION MARKER: All test entities use email domain @wateen-test-seed.local
"""

import random
from decimal import Decimal

from django.contrib.gis.geos import Point, Polygon

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
TEST_EMAIL_DOMAIN = "wateen-test-seed.local"

# Valid Egyptian governorate codes from validators.py
GOVERNORATE_CODES = [
    "01", "02", "03", "04", "11", "12", "13", "14", "15", "16",
    "17", "18", "19", "21", "22", "23", "24", "25", "26", "27",
    "28", "29", "31", "32", "33", "34", "35",
]

# Egyptian mobile prefixes: 010, 011, 012, 015
PHONE_PREFIXES = ["010", "011", "012", "015"]

# Greater Cairo district bounding boxes (lng_min, lat_min, lng_max, lat_max)
# These represent realistic geographic areas for agency coverage zones.
CAIRO_DISTRICTS: dict[str, tuple[float, float, float, float]] = {
    "maadi":        (31.2400, 29.9500, 31.2800, 29.9800),
    "nasr_city":    (31.3200, 30.0500, 31.3700, 30.0800),
    "new_cairo":    (31.3800, 30.0000, 31.4500, 30.0500),
    "6th_october":  (30.9000, 29.9300, 30.9800, 29.9800),
    "zayed":        (30.9800, 30.0000, 31.0400, 30.0400),
    "heliopolis":   (31.3200, 30.0800, 31.3600, 30.1100),
    "downtown":     (31.2300, 30.0400, 31.2600, 30.0600),
    "dokki":        (31.2000, 30.0300, 31.2200, 30.0500),
    "mohandessin":  (31.1900, 30.0500, 31.2100, 30.0700),
    "zamalek":      (31.2100, 30.0550, 31.2300, 30.0700),
    "giza":         (31.1800, 29.9800, 31.2200, 30.0200),
    "shubra":       (31.2300, 30.0700, 31.2600, 30.0950),
}

# Arabic first names (male and female) — used with Faker fallback
ARABIC_FIRST_NAMES_MALE = [
    "أحمد", "محمد", "عمر", "يوسف", "علي", "حسن", "حسين", "إبراهيم",
    "خالد", "طارق", "عبدالله", "كريم", "مصطفى", "سعيد", "فؤاد",
    "ياسر", "هشام", "مروان", "عمرو", "رامي", "ماجد", "وائل",
    "تامر", "شريف", "أسامة", "نادر", "بلال", "سامي", "فارس", "زياد",
]

ARABIC_FIRST_NAMES_FEMALE = [
    "فاطمة", "نور", "سارة", "ياسمين", "مريم", "هدى", "آية", "دينا",
    "رنا", "منى", "نادية", "سلمى", "هبة", "أميرة", "ليلى",
    "نورهان", "شيماء", "إسراء", "رانيا", "داليا", "سمر", "غادة",
    "علا", "مها", "لمياء", "عبير", "ريهام", "منار", "جنى", "ملك",
]

ARABIC_LAST_NAMES = [
    "محمود", "إبراهيم", "حسن", "علي", "عبدالرحمن", "السيد", "أحمد",
    "عثمان", "مصطفى", "يونس", "خليل", "عبدالعزيز", "الشافعي", "فهمي",
    "سالم", "بدر", "توفيق", "رشدي", "جمال", "عبدالحميد", "نصر",
    "صلاح", "حمدي", "شوقي", "منصور", "راشد", "عطية", "حنفي",
]

NURSE_SPECIALIZATIONS = [
    ["تمريض عام"],
    ["عناية مركزة"],
    ["تمريض أطفال"],
    ["تمريض كبار السن"],
    ["علاج طبيعي"],
    ["تمريض جراحي"],
    ["رعاية منزلية"],
    ["تمريض الأمومة"],
    ["تمريض الطوارئ"],
    ["العلاج الوريدي"],
]


# ─────────────────────────────────────────────────────────────────────────────
# Egyptian National ID Generator
# ─────────────────────────────────────────────────────────────────────────────
_national_id_counter = 0


def generate_valid_national_id() -> str:
    """
    Generate a structurally valid 14-digit Egyptian National ID.

    Format: CYYMMDDSSSSGK
      C   = Century (2 = 1900s, 3 = 2000s)
      YY  = Birth year
      MM  = Birth month (01-12)
      DD  = Birth day (01-28, conservative to avoid month-length issues)
      SSSS = Governorate code (2 digits) + sequence (2 digits)
      G   = Gender digit (odd=male, even=female)
      K   = Check digit
    """
    global _national_id_counter
    _national_id_counter += 1

    century = random.choice(["2", "3"])
    year = random.randint(70 if century == "2" else 0, 99 if century == "2" else 25)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Conservative max to pass validator
    governorate = random.choice(GOVERNORATE_CODES)
    # Use counter + random to ensure uniqueness
    sequence = f"{(_national_id_counter % 100):02d}"
    gender = random.randint(0, 9)
    check = random.randint(0, 9)

    national_id = f"{century}{year:02d}{month:02d}{day:02d}{governorate}{sequence}{gender}{check}"
    assert len(national_id) == 14, f"Generated invalid NID length: {national_id}"
    return national_id


def generate_egyptian_phone() -> str:
    """Generate a valid Egyptian mobile phone number (01[0125]XXXXXXXX)."""
    prefix = random.choice(PHONE_PREFIXES)
    suffix = "".join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{prefix}{suffix}"


def generate_test_email(prefix: str) -> str:
    """Generate a test email with the isolation marker domain."""
    return f"{prefix}@{TEST_EMAIL_DOMAIN}"


def generate_arabic_name() -> tuple[str, str]:
    """Generate a random Arabic (first_name, last_name) pair."""
    gender = random.choice(["male", "female"])
    if gender == "male":
        first = random.choice(ARABIC_FIRST_NAMES_MALE)
    else:
        first = random.choice(ARABIC_FIRST_NAMES_FEMALE)
    last = random.choice(ARABIC_LAST_NAMES)
    return first, last


# ─────────────────────────────────────────────────────────────────────────────
# B2B Document Generators
# ─────────────────────────────────────────────────────────────────────────────
def generate_commercial_registry(index: int) -> str:
    """Generate a unique test commercial registry number."""
    return f"TEST-CR-{index:06d}"


def generate_moh_license(index: int) -> str:
    """Generate a unique test MoH license number."""
    return f"TEST-MOH-{index:06d}"


def generate_tax_id(index: int) -> str:
    """Generate a unique test tax ID."""
    return f"TEST-TAX-{index:06d}"


# ─────────────────────────────────────────────────────────────────────────────
# PostGIS Geometry Generators
# ─────────────────────────────────────────────────────────────────────────────
def generate_cairo_polygon(district: str | None = None) -> Polygon:
    """
    Generate a realistic PostGIS Polygon for a Greater Cairo district.

    If no district is specified, one is chosen randomly. The polygon
    represents a sub-area within the district bounding box to simulate
    a realistic agency coverage zone (not the entire district).

    Algorithm:
      1. Pick a district bounding box
      2. Generate a smaller random rectangle within that bbox
      3. Return as a closed GEOS Polygon (SRID 4326)
    """
    if district is None:
        district = random.choice(list(CAIRO_DISTRICTS.keys()))

    bbox = CAIRO_DISTRICTS[district]
    lng_min, lat_min, lng_max, lat_max = bbox

    # Generate a sub-rectangle within the district (60-90% of the bbox)
    scale = random.uniform(0.6, 0.9)
    lng_range = (lng_max - lng_min) * scale
    lat_range = (lat_max - lat_min) * scale

    sub_lng_min = lng_min + random.uniform(0, (lng_max - lng_min) - lng_range)
    sub_lat_min = lat_min + random.uniform(0, (lat_max - lat_min) - lat_range)
    sub_lng_max = sub_lng_min + lng_range
    sub_lat_max = sub_lat_min + lat_range

    # Closed polygon ring (5 points: 4 corners + close)
    ring = (
        (sub_lng_min, sub_lat_min),
        (sub_lng_max, sub_lat_min),
        (sub_lng_max, sub_lat_max),
        (sub_lng_min, sub_lat_max),
        (sub_lng_min, sub_lat_min),  # Close the ring
    )

    return Polygon(ring, srid=4326)


def generate_point_inside_polygon(polygon: Polygon) -> Point:
    """
    Generate a random geographic Point guaranteed to be INSIDE the given Polygon.

    Algorithm (rejection sampling):
      1. Get the polygon's bounding envelope
      2. Generate a random point within the envelope
      3. Check if point is within the polygon using GEOS ST_Within
      4. If not, retry (for convex rectangular polygons, first attempt
         almost always succeeds)

    This ensures spatial integrity: Visit locations will always intersect
    with their assigned Agency's coverage polygon.
    """
    envelope = polygon.envelope
    min_x, min_y, max_x, max_y = envelope.extent

    for _ in range(100):  # Safety limit
        lng = random.uniform(min_x, max_x)
        lat = random.uniform(min_y, max_y)
        point = Point(lng, lat, srid=4326)
        if polygon.contains(point):
            return point

    # Fallback: centroid (should never reach here with rectangular polygons)
    centroid = polygon.centroid
    return Point(centroid.x, centroid.y, srid=4326)


def generate_random_visit_status() -> str:
    """
    Generate a weighted random visit status with realistic distribution.
    ~60% COMPLETED, ~15% IN_PROGRESS, ~10% ACCEPTED, ~10% CANCELLED, ~5% PENDING
    """
    from visits.models import VisitStatus

    statuses = [
        (VisitStatus.COMPLETED, 60),
        (VisitStatus.IN_PROGRESS, 15),
        (VisitStatus.ACCEPTED, 10),
        (VisitStatus.CANCELLED, 10),
        (VisitStatus.PENDING_AGENCY, 3),
        (VisitStatus.PENDING_NURSE, 2),
    ]
    population = [s for s, w in statuses for _ in range(w)]
    return random.choice(population)


def generate_pricing_snapshot() -> dict[str, Decimal]:
    """
    Generate a realistic immutable pricing snapshot for a visit.
    All prices are in EGP (Egyptian Pounds).
    """
    base_price = Decimal(str(random.randint(150, 500)))
    distance_km = Decimal(str(round(random.uniform(1.0, 25.0), 2)))
    distance_rate = Decimal("5.00")
    distance_fee = (distance_km * distance_rate).quantize(Decimal("0.01"))
    time_multiplier = Decimal(str(random.choice(["1.00", "1.25", "1.50"])))
    ai_surge = Decimal("1.00")
    final_price = (
        (base_price + distance_fee) * time_multiplier * ai_surge
    ).quantize(Decimal("0.01"))

    return {
        "base_price": base_price,
        "distance_km": distance_km,
        "distance_rate": distance_rate,
        "distance_fee": distance_fee,
        "time_multiplier": time_multiplier,
        "ai_surge_coefficient": ai_surge,
        "final_price": final_price,
    }
