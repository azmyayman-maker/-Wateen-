import { 
  CannulaFluidsSVG, IronIV_SVG, CatheterFeedingSVG, BloodSamplingSVG,
  InjectionsSVG, VitalsMonitorSVG, WoundCareSVG, StitchRemovalSVG, 
  OxygenMeasurementSVG 
} from '@/components/services/ServicesGrid';

// Theme constants
const THEME = {
  teal:   '22, 97, 95',
  green:  '121, 178, 83',
  red:    '243, 45, 23',
  orange: '253, 136, 57',
};

export type ServiceId = 
  | 'iv-drip' 
  | 'iron-iv' 
  | 'catheters-feeding' 
  | 'blood-sampling' 
  | 'injections' 
  | 'vitals-check' 
  | 'wound-care' 
  | 'post-surgery' 
  | 'oxygen-measurement';

export interface ServiceDetail {
  id: ServiceId;
  nameEn: string;
  nameAr: string;
  descriptionEn: string;
  descriptionAr: string;
  basePrice: number;
  colorRgb: string;
  svg: React.ComponentType<{ className?: string }>;
  tagsEn: string[];
  tagsAr: string[];
  heroType: 'fluid-drops' | 'crimson-pulse' | 'comfort-orange' | 'oxygen-flow' | 'surgical-precision';
}

export const servicesData: Record<ServiceId, ServiceDetail> = {
  'iv-drip': {
    id: 'iv-drip',
    nameEn: 'Cannula & IV Fluids',
    nameAr: 'تركيب الكانيولا والمحاليل',
    descriptionEn: 'Professional insertion of IV cannulas and administration of prescribed fluids for rehydration or medication delivery, ensuring maximum comfort and vein preservation.',
    descriptionAr: 'تركيب احترافي للكانيولا الوريدية وإعطاء المحاليل الموصوفة لتعويض السوائل أو إعطاء الأدوية، مع ضمان أقصى درجات الراحة والحفاظ على الأوردة.',
    basePrice: 150,
    colorRgb: THEME.green,
    svg: CannulaFluidsSVG,
    tagsEn: ['Rehydration', 'Medication', 'Quick Recovery'],
    tagsAr: ['تعويض سوائل', 'إعطاء أدوية', 'تعافي سريع'],
    heroType: 'fluid-drops'
  },
  'iron-iv': {
    id: 'iron-iv',
    nameEn: 'Iron IV (Medical Supervision)',
    nameAr: 'محاليل الحديد (إشراف طبي)',
    descriptionEn: 'Safe administration of intravenous iron therapy to treat anemia, closely monitored by a registered nurse to handle any potential side effects immediately.',
    descriptionAr: 'إعطاء آمن لعلاج الحديد الوريدي لعلاج حالات الأنيميا، تحت إشراف دقيق من ممرض مسجل للتعامل الفوري مع أي آثار جانبية محتملة.',
    basePrice: 350,
    colorRgb: THEME.teal,
    svg: IronIV_SVG,
    tagsEn: ['Anemia Treatment', 'Supervised', 'Vitality Boost'],
    tagsAr: ['علاج الأنيميا', 'إشراف طبي', 'تعزيز الحيوية'],
    heroType: 'fluid-drops'
  },
  'catheters-feeding': {
    id: 'catheters-feeding',
    nameEn: 'Catheters & Feeding Tubes',
    nameAr: 'تركيب القساطر وأنابيب التغذية',
    descriptionEn: 'Expert insertion, care, and removal of urinary catheters and nasogastric feeding tubes, maintaining strict aseptic techniques to prevent infections.',
    descriptionAr: 'تركيب، عناية، وإزالة احترافية للقساطر البولية وأنابيب التغذية الأنفية المعدية، مع الحفاظ على تقنيات تعقيم صارمة لمنع العدوى.',
    basePrice: 200,
    colorRgb: THEME.orange,
    svg: CatheterFeedingSVG,
    tagsEn: ['Urinary Care', 'Enteral Nutrition', 'Sterile Procedure'],
    tagsAr: ['عناية بولية', 'تغذية معوية', 'إجراء معقم'],
    heroType: 'surgical-precision'
  },
  'blood-sampling': {
    id: 'blood-sampling',
    nameEn: 'Home Blood Sampling',
    nameAr: 'سحب عينات الدم بالمنزل',
    descriptionEn: 'Convenient and painless blood sample collection from the comfort of your home, transported safely to partnering certified laboratories.',
    descriptionAr: 'سحب عينات دم مريح وبدون ألم وأنت في راحة منزلك، مع نقل آمن للعينات إلى المعامل المعتمدة الشريكة.',
    basePrice: 120,
    colorRgb: THEME.red,
    svg: BloodSamplingSVG,
    tagsEn: ['Painless', 'Convenient', 'Lab Accurate'],
    tagsAr: ['بدون ألم', 'مريح', 'دقة المعامل'],
    heroType: 'crimson-pulse'
  },
  'injections': {
    id: 'injections',
    nameEn: 'Injections & Allergy Tests',
    nameAr: 'الحقن واختبار الحساسية',
    descriptionEn: 'Administration of Intramuscular (IM), Intravenous (IV), and Subcutaneous (SC) injections, along with crucial pre-injection allergy testing.',
    descriptionAr: 'إعطاء الحقن العضلية والوريدية وتحت الجلد بأمان، مصحوبة باختبارات الحساسية الضرورية قبل الحقن.',
    basePrice: 100,
    colorRgb: THEME.teal,
    svg: InjectionsSVG,
    tagsEn: ['IM/IV/SC', 'Allergy Screened', 'Safe'],
    tagsAr: ['عضلي/وريدي', 'فحص حساسية', 'آمن'],
    heroType: 'comfort-orange'
  },
  'vitals-check': {
    id: 'vitals-check',
    nameEn: 'Blood Sugar & Pressure',
    nameAr: 'قياس نسبة السكر والضغط',
    descriptionEn: 'Routine monitoring of critical vital signs including blood pressure and random/fasting blood sugar to keep track of your health status.',
    descriptionAr: 'متابعة دورية للعلامات الحيوية الهامة بما في ذلك ضغط الدم ونسبة السكر العشوائي أو الصائم للاطمئنان على حالتك الصحية.',
    basePrice: 80,
    colorRgb: THEME.red,
    svg: VitalsMonitorSVG,
    tagsEn: ['Hypertension', 'Diabetes', 'Routine Care'],
    tagsAr: ['ضغط الدم', 'السكري', 'رعاية دورية'],
    heroType: 'crimson-pulse'
  },
  'wound-care': {
    id: 'wound-care',
    nameEn: 'Wound Care & Diabetic Foot',
    nameAr: 'العناية بالجروح والقدم السكري',
    descriptionEn: 'Advanced care and dressing for surgical wounds, bedsores, and critical diabetic foot conditions to accelerate healing and prevent severe complications.',
    descriptionAr: 'رعاية وتغيير متقدم للجروح الجراحية، قرح الفراش، وحالات القدم السكري الحرجة لتسريع الشفاء ومنع المضاعفات الخطيرة.',
    basePrice: 220,
    colorRgb: THEME.orange,
    svg: WoundCareSVG,
    tagsEn: ['Surgical Wounds', 'Diabetic Foot', 'Bedsores'],
    tagsAr: ['جروح جراحية', 'قدم سكري', 'قرح فراش'],
    heroType: 'comfort-orange'
  },
  'post-surgery': {
    id: 'post-surgery',
    nameEn: 'Post-Surgery & Stitch Removal',
    nameAr: 'متابعة ما بعد الجراحة وفك الغرز',
    descriptionEn: 'Comprehensive post-operative home monitoring and safe removal of surgical stitches or staples once the healing period is complete.',
    descriptionAr: 'متابعة منزلية شاملة لما بعد العمليات الجراحية، وإزالة آمنة لغرز أو دبابيس الجراحة بمجرد اكتمال فترة الالتئام.',
    basePrice: 180,
    colorRgb: THEME.teal,
    svg: StitchRemovalSVG,
    tagsEn: ['Post-Op Care', 'Stitch Removal', 'Healing'],
    tagsAr: ['رعاية ما بعد العمليات', 'فك غرز', 'التئام'],
    heroType: 'surgical-precision'
  },
  'oxygen-measurement': {
    id: 'oxygen-measurement',
    nameEn: 'Home Oxygen Measurement',
    nameAr: 'قياس نسبة الأكسجين بالمنزل',
    descriptionEn: 'Accurate measurement of blood oxygen saturation (SpO2) and respiratory assessment for patients with pulmonary conditions.',
    descriptionAr: 'قياس دقيق لنسبة تشبع الأكسجين في الدم (SpO2) وتقييم للحالة التنفسية للمرضى الذين يعانون من حالات رئوية.',
    basePrice: 80,
    colorRgb: THEME.green,
    svg: OxygenMeasurementSVG,
    tagsEn: ['SpO2', 'Respiratory', 'Pulmonary Care'],
    tagsAr: ['تشبع الأكسجين', 'جهاز تنفسي', 'رعاية رئوية'],
    heroType: 'oxygen-flow'
  }
};
