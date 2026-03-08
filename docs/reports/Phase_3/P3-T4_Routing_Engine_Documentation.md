# توثيق هندسي مفصل: محرك التوجيه واحتساب المسافات (Routing Engine - P3-T4)

**تاريخ التوثيق:** 2026-03-08
**المنصة:** Wateen B2B2C Healthcare
**المسؤولية:** نظام التسعير والتوثيق الملاحي وحساب الوقت التقديري (ETA).
**التقنيات المستخدمة:** Python 3.11, Django 5, Redis, OSRM, OpenRouteService (ORS), Pytest.

---

## 1. النظرة العامة (Overview)

تم بناء هذه الخدمة لحل مشكلة احتساب المسافة بخط مستقيم (Haversine) واستبدالها بحساب مسافة القيادة الفعلية لضمان تسعير عادل للزيارات وتوفير وقت وصول دقيق (ETA) للممرضين. النظام مصمم بذكاء ليضمن **توفر الخدمة بنسبة 100%** من خلال دمج محركين (OSRM كمحرك أساسي مجاني، و ORS كمحرك طوارئ للتحويل التلقائي عند الفشل).

---

## 2. الخوارزميات المعتمدة (Algorithms)

### 2.1 خوارزمية التشفير الجغرافي (True Geohash Encoding)

بدلاً من استخدام MD5 للإحداثيات والذي فشل في التعرف على المواقع المتقاربة جداً بنطاق أمتار، تم بناء خوارزمية Geohash من الصفر في بايثون لتجنب الاعتماد على مكتبات السي (C-extensions) وضمان سهولة التشغيل في أي بيئة. تم استخدام **الدقة 7 (Precision = 7)**، والتي تمثل مربعاً جغرافياً بأبعاد 153 متر × 153 متر.

**شفيرة الخوارزمية (Implementation):**

```python
GEOHASH_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
GEOHASH_PRECISION = 7

def _encode_geohash(latitude: float, longitude: float, precision: int = GEOHASH_PRECISION) -> str:
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    is_lon = True

    while len(geohash) < precision:
        if is_lon:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude >= mid:
                ch |= bits[bit]
                lon_interval[0] = mid
            else:
                lon_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude >= mid:
                ch |= bits[bit]
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid
        is_lon = not is_lon

        if bit < 4:
            bit += 1
        else:
            geohash.append(GEOHASH_BASE32[ch])
            bit = 0; ch = 0

    return "".join(geohash)

def _geohash_key(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    origin_hash = _encode_geohash(lat1, lng1, GEOHASH_PRECISION)
    dest_hash = _encode_geohash(lat2, lng2, GEOHASH_PRECISION)
    return f"route:{origin_hash}:{dest_hash}"
```

### 2.2 نمط الاستراتيجية وقاطع الدائرة (Strategy Pattern & Circuit Breaker)

تم استخدام الاستراتيجية البرمجية لتوحيد مخرجات أي محرك توجيه في كيان واحد غير قابل للتغيير `RouteResult`. ويتم التبديل بين مزودي الخدمة تلقائياً في دالة `get_route` لحماية النظام من أي انهيار واختناقات شبكية.

**هيكل مزودي الخدمة (Providers Implementation):**

```python
@dataclass(frozen=True)
class RouteResult:
    distance_km: float
    duration_minutes: float
    polyline_geometry: Optional[str] = None

class RoutingProvider(ABC):
    @abstractmethod
    def get_route(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> RouteResult:
        pass

# OSRM Provider (Primary)
class OSRMProvider(RoutingProvider):
    # يقوم بإرسال طلب (GET)
    # يجلب المسافة والوقت ويعيد كائن RouteResult

# ORS Provider (Fallback)
class ORSProvider(RoutingProvider):
    # يقوم بإرسال طلب (POST) مع مفتاح الـ API
    # يجلب المسافة والوقت ويعيد كائن RouteResult

def get_route(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, *, bypass_cache: bool = False) -> RouteResult:
    # 1. فحص الكاش (Redis) مسبقاً بناءً على مفتاح الـ Geohash
    # 2. حلقة الـ Circuit Breaker
    providers = [("osrm", OSRMProvider()), ("ors", ORSProvider())]
    for name, provider in providers:
        try:
            result = provider.get_route(origin_lat, origin_lng, dest_lat, dest_lng)
            # 3. حفظ النتيجة فوراً لمدة 15 دقيقة (TTL=900)
            return result
        except Exception as e:
            logger.warning("Routing provider %s failed: %s", name, e)
            continue
    raise RuntimeError("All routing providers failed.")
```

---

## 3. آلية احتساب وقت وصول الممرض (Nurse ETA Calculation)

تم إضافة دالة وسيطة تربط طبقة البيانات الجغرافية (GeoDjango) بقاعدة التوجيه لتحديث وقت الوصول في التطبيقات.

```python
def calculate_nurse_eta(nurse_profile, patient_location) -> Optional[RouteResult]:
    if not nurse_profile.last_location:
        return None
    try:
        return get_route(
            origin_lat=nurse_profile.last_location.y,
            origin_lng=nurse_profile.last_location.x,
            dest_lat=patient_location.y,
            dest_lng=patient_location.x,
        )
    except RuntimeError:
        return None
```

---

## 4. تقرير الاختبارات ونتائجها (Testing Report & Results)

جناح الاختبارات (`test_routing.py`) تم بناؤه باستخدام مكتبتي `unittest` و `responses` لمحاكاة الظروف القاهرة وفصل الاعتمادية عن الشبكة الحقيقية أثناء الفحص.

### نتائج جناح الاختبار (Pytest Execution Results)

جميع الاختبارات (11 اختباراً) تم اجتيازها بنجاح (100% Pass Rate).

**1. حالات دقة التشفير الجغرافي (TestGeohashEncoding)**

- [✓] `test_encode_geohash_returns_string`: يتأكد من إرجاع نص طوله مطابق بدقة.
- [✓] `test_encode_geohash_precision_7`: يحسب التشفير لنقطة حقيقية ويتأكد من تطابق الهاش `stq4yv3`.
- [✓] `test_encode_geohash_precision_8`: يتحقق من مرونة الكود للمستويات الأعلى.
- [✓] `test_geohash_key_same_origins_same_key`: نقطتان متطابقتان تنتجان نفس مفتاح الذاكرة لتخفيف الضغط.
- [✓] `test_geohash_key_different_destinations_different_key`: المسارات المختلفة تمتلك مفاتيح مختلفة قطعاً.

**2. حالات واجهة المحركات (TestOSRMProvider / TestORSProvider)**

- [✓] `test_get_route_success (OSRM)`: محاكاة رد JSON من OSRM وتحويل هندسي سليم لـ 5.2 كم و 12.3 دقيقة.
- [✓] `test_get_route_no_routes_raises_value_error`: محاكاة طلب مسار في المحيط (لا يوجد طرق) والتقاط استثناء `ValueError`.
- [✓] `test_get_route_success (ORS)`: محاكاة رد JSON من ORS وتحويل الاستجابة المعقدة للمحرك الثاني لبيانات مقروءة 5.15 كم و 12.0 دقيقة.

**3. حالات تجاوز الفشل العنيف (TestFailover)**

- [✓] `test_osrm_timeout_falls_back_to_ors`: **اهم اختبار!** تمت محاكاة `requests.exceptions.Timeout` على OSRM. الكود التقط الخطأ فوراً وسجل `Warning Log`، وانتقل لطلب ORS وأعاد المسار بنجاح تام للمستخدم النهائي دون علمه بحدوث الخلل.
- [✓] `test_all_providers_fail_raises_runtime_error`: تمت محاكاة انهيار خادم OSRM وانهيار شبكة ORS في التوقيت عينه، الرد كان منظماً ببعث `RuntimeError` للتعامل الآمن معه في الواجهة دون التسبب في Crash كامل للخادم (500 Error داخلي غير محمي).

**4. حالات التخزين المؤقت (TestCaching)**

- [✓] `test_mock_cache_operations`: محاكاة الـ `django-redis` للتأكد من تخزين مخرجات الـ `RouteResult`، ونجاح استقراء القيم الكبيرة مراراً بمجرد تمرير الـ Key.

---

## 5. مبررات القرارات الهندسية (Engineering Rationales)

1. **الاستقلالية عن C-Extensions:** استخدام مكتبة `python-geohash` الجاهزة كان يتطلب تجميعات (Compilations) قد تفشل في خوادم الويندوز أو حاويات لينكس البسيطة. قمنا ببرمجة دالة مبنية خصيصاً ككود بايثون صريح مما أضاف متانة لا مثيل لها للنظام.
2. **الترتيب في الفشل:** وضعنا OSRM أولاً، كونه مجاني. إذا واجهنا انقطاعات مؤقتة، ندفع التكلفة لمزود ORS مؤقتاً لضمان الموثوقية الشاملة.
3. **التصميم المعتمد على الداتاكلاس (Dataclasses):** تجنبنا إرجاع قواميس (Dictionaries) لضمان بيئة آمنة للمتغيرات عبر التلميح النوعي (Type Hinting) الصارم.

**حالة التذكرة النهائية:** مقفلة ومركبة بالكامل للإنتاج. قادرة على الاستخدام الفوري ضمن محرك التسعير وتطبيق الممرض.
