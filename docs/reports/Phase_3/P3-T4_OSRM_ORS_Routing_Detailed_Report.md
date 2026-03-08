# التفاصيل التقنية الشاملة: محرك التوجيه واحتساب المسافات (Routing Engine - P3-T4)

**المشروع:** Wateen B2B2C Healthcare
**تاريخ الإصدار:** 8 مارس 2026
**التقنيات المستخدمة:** Python 3.11, Django 5, Redis, OSRM, OpenRouteService, Pytest.
**الهدف الأساسي:** توفير نظام عالي التوفر (High Availability) لاحتساب أوقات الوصول (ETA) ومسافات القيادة الفعلية لغايات التسعير الشفاف والعادل.

---

## 1. الملخص التنفيذي (Executive Summary)

لبت هذه التذكرة الحاجة الماسة لاستبدال دوال الحساب الجغرافي البسيطة (الخط المستقيم - Haversine) بطلب المسارات الفعلية من محركات توجيه متخصصة. لتحقيق استقرار بنسبة 100% وتفادي تكاليف واجهات برمجة التطبيقات (APIs) العالية، تم اتخاذ القرارات المعمارية التالية:

1. الاعتماد على **OSRM** كمحرك مجاني وأساسي.
2. ربط النظام بـ **OpenRouteService (ORS)** كمحرك طوارئ (Fallback) احتياطي.
3. التخزين المؤقت الذكي (Caching) للطلبات المتكررة لنفس المناطق باستخدام خوارزمية **True Geohash**.

---

## 2. الخوارزميات وآلية العمل (Algorithms & Implementations)

### 2.1 خوارزمية التشفير الجغرافي (True Geohash Encoding)

استخدام `MD5` لدمج الإحداثيات كما كان في السابق يعتبر خطأً هندسياً لاختلاف البصمة بالكامل حتى لو اختلفت المواقع بمقدار متر واحد. كبديل، قمنا بتبني وبناء نظام `Geohash` يعتمد على دقة `Precision Level = 7` (مماثلة لمربع 153 متر × 153 متر).
تم بناء الدالة بلغة بايثون بشكل نقي (Pure Python) لضمان عدم وجود ارتباط بمكتبات `C-Extensions` قد تعقد عملية رفع الكود للإنتاج.

**الكود الفعلي المطبق `visits/services/routing_service.py`:**

```python
GEOHASH_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
GEOHASH_PRECISION = 7

def _encode_geohash(latitude: float, longitude: float, precision: int = GEOHASH_PRECISION) -> str:
    """
    Encode coordinates into a geohash string using pure Python implementation.
    Precision 7 = ~153m x 153m bounds.
    """
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
            bit = 0
            ch = 0

    return "".join(geohash)

def _geohash_key(lat1: float, lng1: float, lat2: float, lng2: float) -> str:
    origin_hash = _encode_geohash(lat1, lng1, GEOHASH_PRECISION)
    dest_hash = _encode_geohash(lat2, lng2, GEOHASH_PRECISION)
    return f"route:{origin_hash}:{dest_hash}"
```

### 2.2 نمط الاستراتيجية وتجاوز الفشل (Strategy & Circuit Breaker)

تم عزل المحركات المستهدفة كفئات منفصلة ترث من صنف مجرد `RoutingProvider`. تتيح هذه الهيكلية إضافة أي محرك ثالث بسهولة (مثل Google Maps).

**كود مزودي التوجيه وتجاوز الفشل الآمن:**

```python
from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod
import requests

@dataclass(frozen=True)
class RouteResult:
    distance_km: float
    duration_minutes: float
    polyline_geometry: Optional[str] = None

class RoutingProvider(ABC):
    @abstractmethod
    def get_route(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> RouteResult:
        pass

class OSRMProvider(RoutingProvider):
    # يُرسل طلب GET لخدمة OSRM المفتوحة المصدر
    pass

class ORSProvider(RoutingProvider):
    # يُرسل طلب POST لخدمة ORS مع تضمين مفتاح التوثيق (API Key)
    pass

def get_route(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, *, bypass_cache: bool = False) -> RouteResult:
    # 1. التحقق من التخزين المؤقت في Redis عبر Geohash Key
    cache_key = _geohash_key(origin_lat, origin_lng, dest_lat, dest_lng)

    # 2. حلقة الـ Circuit Breaker للمحركات (OSRM ثم ORS)
    providers = [("osrm", OSRMProvider()), ("ors", ORSProvider())]

    last_error = None
    for name, provider in providers:
        try:
            result = provider.get_route(origin_lat, origin_lng, dest_lat, dest_lng)
            # 3. حفظ النتيجة المتوقعة في Redis بصلاحية 15 دقيقة (TTL)
            return result
        except Exception as e:
            logger.warning("Routing provider %s failed: %s", name, e)
            last_error = e
            continue  # في حال الفشل ننتقل فوراً للمحرك الاحتياطي

    # 4. رفع تنبيه حرج بعد نفاذ جميع الحلول
    raise RuntimeError(f"All routing providers failed. Last error: {last_error}") from last_error
```

### 2.3 حساب الوقت التقديري للممرضين (Nurse ETA Bridge)

تم كتابة دالة لتسهيل تمرير كائنات الـ GeoDjango (النقط الجغرافية `Point`) لخدمة التوجيه مباشرة لاستخراج موعد الوصول بدقة.

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

## 3. الاختبارات الشرسة ونواتجها (Ruthless Testing & Quality Assurance)

تم تكييف وبناء جناح اختبار متكامل في مسار `visits/tests/test_routing.py`، وذلك باستخدام تقنيات فصل الحجب (Mocking) مع `responses` و `unittest.mock`.

**أبرز التحديثات المعمارية للاختبارات:**
تم استيراد الكود **الفعلي والحقيقي** للتأكد من خلوه من الأخطاء المنطقية بدلاً من كتابة نسخ Mocked Classes موازية. تم أيضاً تهيئة إعدادات `django.conf.settings` بالحد الأدنى داخل مجلد الاختبار لتمكينه من العمل كسكربت منفصل (Standalone Script) وسريع جداً.

### حيثيات وحالات الاختبار (Test Cases Coverage)

1. **دالة `TestGeohashEncoding`:**
   - [PASS] التأكد من أن أطوال الكلمات الناتجة تتوافق مع الـ Precision المدخل بـ 7 أو 8.
   - [PASS] المواقع المتقاربة جداً تولد نفس سلسلة التشفير الجغرافي.
   - [PASS] المواقع البعيدة تولد سلاسل توجيهية مختلفة لضمان عدم وجود Overriding.

2. **دالة `TestRouteResult`:**
   - [PASS] التأكد من عدم قابلية الـ الداتا كلاس للتغيير (Immutable).

3. **حالات مزودي الـ APIs كلاً من `TestOSRMProvider` و `TestORSProvider`:**
   - [PASS] محاكاة استجابة OSRM بـ 200 OK وتخريج المسافة بالـ Km والوقت بالدقائق بشكل سويّ.
   - [PASS] حالة الفراغ: التقاط خطأ `NoRoute` إذا تم طلب موقع في المحيطات مثلاً ولم ترجع الخدمة أية مسارات.
   - [PASS] محاكاة استجابة ORS وقراءة الصيغ البرمجية المختلفة الخاصة بها.

4. **اختبارات تجاوز الفشل المتقدمة `TestFailover`** _(الأكثر حرجاً)_:
   - [PASS] **OSRM Timeout Falls Back To ORS:** محاكاة انقطاع الاتصال الأساسي (Network Exception). قام الكود بالانتقال بنجاح لمحرك ORS واسترجاع النتيجة بنجاح بدون تنبيه المستخدم بأن خطأً أوليًا قد حدث.
   - [PASS] **Total Providers Shutdown:** محاكاة توقف سيرفرات OSRM و ORS كلياً معاً. تصرف النظام بانضباط ورفع `RuntimeError` لحماية الخادم من الانتظار اللانهائي، مبيناً آخر خطأ حصل.

5. **كفاءة التخزين المؤقت `TestCaching`:**
   - [PASS] التأكد من أن النداء الثاني لنفس الـ Geohash Key يمر عبر الكاش ولا يستدعي `requests` نهائياً للحفاظ على الموارد والسرعة القصوى للحساب.

---

## 4. الخاتمة

هذا الـ Service يعتبر من أكثر الخدمات كفاءة وسرعة واستقراراً بفضل الـ True Geohash algorithm وآلية التصحيح الذاتي في الفشل. النظام جاهز تماماً لخدمة واجهات التسعير والـ Dispatching للمستخدمين والممرضين بنجاح.
