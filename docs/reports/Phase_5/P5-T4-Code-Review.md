# المراجعة المعمارية والبرمجية الشاملة - نظام البث المباشر [P5-T4]

**التاريخ:** 26 مارس 2026
**المراجع:** الوكيل الرئيسي (Main Orchestrator)
**النطاق:** أكواد الواجهة الخلفية (Django Channels, Redis, PostGIS) وواجهات المستخدم (React/Next.js).

---

## 1. التقييم المعماري العام (Architectural Assessment)
تم تصميم البنية التحتية لتكون "Nervous System" قوي، حيث نجح الكود في تطبيق مبادئ (Demand-Driven Architecture).
- **التوافق المالي:** الالتزام الصارم باستخدام `Decimal` مع دوال `Coalesce` و `Sum` لضمان دقة الإيرادات الحية (Escrowed/Settled).
- **التشريعات والخصوصية:** استخدام `ST_SnapToGrid` محيطاً بإحداثيات الـ PostGIS للامتثال للقانون 151/2020، مما يمنع تسريب مواقع المرضى والممرضين بشكل صريح على خريطة الـ SuperAdmin.

---

## 2. الملاحظات الدقيقة ونقاط التحسين (Vulnerabilities & Refactoring)

### أولاً: الواجهة الخلفية (Backend & Django Channels)
1. **تسرب المهام عند الانقطاع (Task Cancellation Leak):**
   - **الخطأ المحتمل:** في ملف `agency_consumer.py` و `superadmin_consumer.py`، نستخدم `self.heartbeat_task.cancel()` عند الـ `disconnect`. هذا يثير استثناء `asyncio.CancelledError` داخل حلقة البث (`broadcast_heartbeat_loop`). ولأن الحلقة غير مغلفة بـ `try...except asyncio.CancelledError`، سيحدث تلوث في سجلات مراقبة الأخطاء (Log Pollution).
   - **الحل:** تغليف منطق الحلقة بالكامل والتعامل مع الاستثناء لإنهاء العملية بهدوء. (Graceful shutdown).

2. **أقفال Redis المتشردة (Zombie Redis Counters):**
   - **الخطأ المحتمل:** في `connection_tracker.py`، نستخدم `incr` و `decr` لضبط حد الاتصالات الأقصى (5 لكل وكالة). ولكن، إذا تعرض خادم (Daphne/Uvicorn) لانهيار مفاجئ (Pod Crash) ولم يتم استدعاء `disconnect`، سيبقى العداد معلقاً حتى تنتهي صلاحيته (بعد 24 ساعة). هذا قد يحرم مدراء الوكالات من الدخول للنظام ظناً منه أنهم استنفدوا الحد الأقصى.
   - **الحل الاحترافي:** استبدال الـ Counter بـ `Redis Sorted Set (ZSET)` حيث يكون الـ `Score` هو التوقيت (Timestamp)، وتقوم الحلقة (Heartbeat loop) بتحديث نبضها المستمر. هكذا، أي اتصال يموت ينتهي من الـ Redis تلقائياً خلال 15 ثانية.

3. **حماية الـ Mutex Lock (Race Condition Buffer):**
   - **الملاحظة:** مدة قفل `LOCK_TIMEOUT` في الـ `CacheShield` هي 5 ثوانٍ. في حالات الضغط الشديد وقت الذروة (Surge Hours)، إذا استغرق استعلام قاعدة البيانات أكثر من 5 ثوانٍ، سيتم فتح القفل وسيسمح لعميل آخر بالاستعلام، مما يدمر فكرة الدرع بالكامل.
   - **الحل:** ربط زمن القفل بمتوسط زمن استجابة `metrics_engine.py` (والذي نراقبه عبر OpenTelemetry) وإضافة هامش أمان منطقي.

### ثانياً: واجهات المستخدم (Frontend & React)
1. **الاستهلاك غير المنضبط في Fallback (Memory Leak Risk):**
   - **الملاحظة:** في `useDashboardSocket.ts`، يتواجد الاعتماد `[agencyId, token, isPolling, error]` في دالة الـ `useEffect`. عند كل تغيير، يتم هدم الـ `setInterval` وإعادة خلقه.
   - **الحل:** فصل منطق الـ HTTP Polling في `useEffect` مستقل يعتمد فقط على `isPolling`، لضمان استقرار دورة حياة المتصفح وعدم هدر الموارد.
2. **بروتوكول الـ WebSocket الفرعي (Subprotocol Echo):**
   - **الملاحظة:** واجهة React تمرر الـ Token داخل المصفوفة `new WebSocket(url, [token])`. هذه تقنية ممتازة وآمنة، لكن يجب التأكد من ضبط الـ Load Balancer (مثل Nginx) للسماح بتمرير ترويسة `Sec-WebSocket-Protocol` دون فلترتها.

---

## 3. التقييم الأمني (Security Audit)
- **المصادقة:** إزالة التوكن من رابط الـ URL عبر `JWTAuthMiddleware` يمنع تسجيل الـ Tokens في الـ Access Logs وهو تطبيق قياسي لسرية النظام.
- **التخريب المتعمد (socket spam):** الاستعانة بـ `if text_data or bytes_data: await self.close(code=1008)` ممتاز جداً لغلق الباب أمام مهاجمي حقن البيانات (Payload Injection) عبر المقابس. النظام مصمم ليكون "للقراءة فقط".

## الخلاصة والتوصية
الكود مهندس بعناية فائقة ويعكس خبرة مؤسسية (Enterprise-Grade). للوصول للدرجة النهائية للاعتماد، **أوصي بشدة** بتصحيح النقاط المذكورة وتحديثات הـ (Zombie Counters) لضمان بيئة قابلة للتوسع اللانهائي دون أي خلل طارئ (Zero-Downtime Resilience).
