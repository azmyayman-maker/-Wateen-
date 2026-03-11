# تقرير هندسة التوزيع التلقائي (Auto-Dispatch Engineering Report) - P4-T4

**تاريخ الإصدار:** مارس 2026  
**الخدمة المصغرة (Microservice):** `visits`  
**التقنيات المستخدمة:** Django 5, PostGIS 3.4, PostgreSQL 16, Celery 5, Redis 7, Django Channels, \`select_for_update(nowait=True)\`

---

## 1. الملخص التنفيذي (Executive Summary)

تم بنجاح إنجاز تذكرة التوزيع التلقائي المكاني `[P4-T4]` كجزء أساسي من محرك Wateen B2B2C. النظام يعالج التحدي المعماري لاختيار أقرب الممرضات المتاحات وتوزيع العروض عليهن في وقت واحد (Broadcast)، مع ضمان الحماية المطلقة ضد حالات التزامن (Race Conditions) وتوجيه الزيارات للوكالة التالية (Re-routing) في حال عدم وجود تجاوب.

---

## 2. الهيكلية المعمارية والخوارزميات (Architecture & Algorithms)

### 2.1 البحث المكاني المدمج مع B2B2C
تم استخدام PostGIS لتنفيذ خوارزمية Nearest-Neighbor K (NN-K) عبر دالة \`Distance()\`:
- يتم تصفية الممرضات لضمان **B2B2C Compliance**: الممرضة يجب أن تتبع للوكالة (\`agency_id\`) التي تم إسناد الزيارة لها في خطوة المزايدة (Bidding).
- يتم جلب أقرب 5 ممرضات بناءً على إحداثيات موقع الزيارة.

### 2.2 الحماية ضد التزامن (Race Condition Guard)
مع إرسال العروض לـ 5 ممرضات، هناك خطر (Race Condition) أن تقبل أكثر من ممرضة العرض في نفس اللحظة (Millisecond).
**الحل (PostgreSQL Row-level Locks):**
تم استخدام \`select_for_update(nowait=True)\` على سجل الـ \`DispatchOffer\`.
- الممرضة الأسرع (Thread A) تحصل على الـ Lock الحصري وتقوم بإتمام قبول الزيارة.
- أي ممرضة أخرى (Thread B) تحاول القبول في اللحظة الزمنية ذاتها ستواجه \`OperationalError\` لأن قاعدة البيانات تمنع الطابور (No-wait) لترجيع استجابة \`409 Conflict\` فورية، مما يوفر أداءً مثالياً (Zero-blocking).

---

## 3. دورة حياة العرض والتوجيه الذكي (Lifecycle & Re-routing)

\`\`\`mermaid
stateDiagram-v2
    [*] --> PENDING_AGENCY : Re-route (Celery)
    PENDING_AGENCY --> AUTO_DISPATCH : Match & Distance Check
    AUTO_DISPATCH --> OFFERS_SENT : max 5 Nurses
    OFFERS_SENT --> ACCEPTED : 1st Nurse wins
    OFFERS_SENT --> REJECTED : Early Re-route (if all 5 reject)
    OFFERS_SENT --> EXPIRED : 60s Timeout (check_dispatch_timeout)
    EXPIRED --> PENDING_AGENCY : Bounce to Next Ranked Agency
\`\`\`

1. **الرفض المبكر (Early Rejection):** إذا تم رفض العرض من كافة الممرضات الـ 5 قبل انتهاء مهلة الـ 60 ثانية، يقوم النظام باستدعاء \`re_route_visit\` بشكل آلي ومبكر للحفاظ على أرواح المرضى وتقليل وقت المعالجة.
2. **الانتهاء الآمن (Timeout Escalation):** تقوم مهمة Celery مبرمجة سلفاً بالتأكد أن العروض منتهية الصلاحية وتقوم بتوجيه الطلب بشكل "Idempotent" لتجنب عمليات الإلغاء الخاطئة. يتم نقل الطلب للوكالة التي تليها في الترتيب مع تحديث المتغير \`reroute_attempts\`.

---

## 4. التعقيد الزمني (Time Complexity Analyzer)

| العملية | Big-O Limit | الملاحظات |
|---------|-------------|-----------|
| البحث المكاني Spatial Search | \`O(N log K)\` | حيث \`N\` الممرضات المتاحات لوكالة و \`K=5\`. استخدام GiST Index على PostGIS |
| القفل والتزامن Lock & Concurrency | \`O(1)\` | زمن الاستجابة فوري في حال الرفض نظراً لخاصية \`nowait=True\` |
| مهمات الخلفية (FCM/WebSockets) | \`O(1)\` | Time decoupled completely into Celery queues |

---

## 5. حالة الفحص والاختبار (QA & Testing Status)

تمت تغطية النظام بسلسلة من الاختبارات الآلية باستخدام Pytest مع الـ Django DB Transactions:
- ✅ **Test US1 (Spatial):** دقة الفلترة المكانية والمطابقة الصارمة مع قواعد B2B2C.
- ✅ **Test US2 (Concurrency):** اختراق Endpoint بـ 5 خيوط معالجة متزامنة. النتيجة: 1 نجاح، 4 فشل آمن.
- ✅ **Test US3 (Early-reject):** إجبار دورة مبكرة على العمل وتقصي استجابة Celery.
- ✅ **Test US4 (Lifecycle):** دورة انتهاء التوقيت وانتقال المعالجة (Timeout and Agency Reroute).

---
**Approval:** ✅ Multi-Agent Orchestrator
