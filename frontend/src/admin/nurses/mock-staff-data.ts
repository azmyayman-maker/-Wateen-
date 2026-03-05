export type StaffStatus = "متاح للتوجيه" | "في زيارة نشطة" | "غير متصل";

export interface StaffDossier {
  id: string;
  name: string;
  specialization: string;
  status: StaffStatus;
  nationalId: string;
  syndicateNumber: string;
  experience: number;
  rating: number;
  totalRevenueGenerated: number;
  completedVisits: number;
  avatarUrl: string;
  currentAssignment?: { patientLocation: string; eta: string; service: string };
  recentActivity: Array<{ id: string; date: string; action: string; status: "success" | "warning" }>;
}

export const staffDossierData: StaffDossier[] = [
  {
    id: "NUR-1001",
    name: "أخصائي / مصطفى عبد الرحمن",
    specialization: "رعاية مركزة وطوارئ",
    status: "في زيارة نشطة",
    nationalId: "29408151234567",
    syndicateNumber: "NUR-88492",
    rating: 4.8,
    totalRevenueGenerated: 85000,
    completedVisits: 142,
    experience: 12,
    avatarUrl: "/avatars/male_nurse.png",
    currentAssignment: {
      patientLocation: "مدينة نصر - الحي السابع",
      eta: "15 دقيقة",
      service: "متابعة جهاز تنفس صناعي منزلي",
    },
    recentActivity: [
      { id: "ACT1", date: "2024-05-18 10:30 AM", action: "تقييم حالة تنفسية - تمت بنجاح", status: "success" },
      { id: "ACT2", date: "2024-05-17 08:15 PM", action: "غيار طبي على جرح سكري", status: "success" },
      { id: "ACT3", date: "2024-05-16 02:00 PM", action: "تأخير في الوصول - زحام مروري", status: "warning" },
      { id: "ACT4", date: "2024-05-15 11:00 AM", action: "تركيب قسطرة بولية", status: "success" },
      { id: "ACT5", date: "2024-05-14 09:30 AM", action: "فحص روتيني وعلامات حيوية", status: "success" },
    ],
  },
  {
    id: "NUR-1002",
    name: "أخصائية / فاطمة حسن",
    specialization: "رعاية مبتسرين وحديثي ولادة",
    status: "متاح للتوجيه",
    nationalId: "28911059876543",
    syndicateNumber: "NUR-77321",
    rating: 4.9,
    totalRevenueGenerated: 120500,
    completedVisits: 315,
    experience: 8,
    avatarUrl: "/avatars/female_nurse.png",
    recentActivity: [
      { id: "BCT1", date: "2024-05-18 09:00 AM", action: "إنهاء شيفت رعاية 12 ساعة", status: "success" },
      { id: "BCT2", date: "2024-05-17 09:00 PM", action: "بدء شيفت رعاية 12 ساعة", status: "success" },
      { id: "BCT3", date: "2024-05-15 10:00 AM", action: "متابعة رضاعة وعلامات حيوية للرضيع", status: "success" },
      { id: "BCT4", date: "2024-05-14 01:30 PM", action: "إعطاء أدوية وريدية حسب الوصفة", status: "success" },
      { id: "BCT5", date: "2024-05-12 11:00 AM", action: "جلسة إرشاد للأم", status: "success" },
    ],
  },
  {
    id: "NUR-1003",
    name: "فني تمريض / كريم سامي",
    specialization: "رعاية مسنين وأمراض مزمنة",
    status: "متاح للتوجيه",
    nationalId: "29103221239876",
    syndicateNumber: "NUR-55210",
    rating: 4.7,
    totalRevenueGenerated: 62000,
    completedVisits: 89,
    experience: 15,
    avatarUrl: "/avatars/male_nurse.png",
    recentActivity: [
      { id: "CCT1", date: "2024-05-18 01:00 PM", action: "متابعة ضغط وسكر منزلي", status: "success" },
      { id: "CCT2", date: "2024-05-16 11:00 AM", action: "إعطاء حقن عضلية ووريدية", status: "success" },
      { id: "CCT3", date: "2024-05-14 04:00 PM", action: "إلغاء الموعد بناء على طلب المريض", status: "warning" },
      { id: "CCT4", date: "2024-05-13 02:00 PM", action: "تغيير على قرحة فراش للدرجة الأولى", status: "success" },
      { id: "CCT5", date: "2024-05-11 10:00 AM", action: "مرافقة مريض فاقد للحركة", status: "success" },
    ],
  },
  {
    id: "NUR-1004",
    name: "ممرض / أحمد محمود",
    specialization: "سحب عينات وتركيب كانيولا",
    status: "غير متصل",
    nationalId: "29507119871234",
    syndicateNumber: "NUR-44198",
    rating: 4.5,
    totalRevenueGenerated: 34000,
    completedVisits: 210,
    experience: 5,
    avatarUrl: "/avatars/male_nurse.png",
    recentActivity: [
      { id: "DCT1", date: "2024-05-17 11:30 AM", action: "سحب عينات دم شاملة", status: "success" },
      { id: "DCT2", date: "2024-05-17 09:00 AM", action: "تركيب كانيولا وريدية", status: "success" },
      { id: "DCT3", date: "2024-05-16 12:00 PM", action: "سحب عينة بصمة القدم للمبتسرين", status: "success" },
      { id: "DCT4", date: "2024-05-15 03:00 PM", action: "صعوبة في تركيب الكانيولا - تم الاستعانة بمشرف", status: "warning" },
      { id: "DCT5", date: "2024-05-14 08:30 AM", action: "توصيل عينات دقيقة للمعمل المركزي", status: "success" },
    ],
  },
  {
    id: "NUR-1005",
    name: "أخصائية / هدى إبراهيم",
    specialization: "تمريض باطنة وجراحة عامة",
    status: "في زيارة نشطة",
    nationalId: "28812041235678",
    syndicateNumber: "NUR-11994",
    rating: 5.0,
    totalRevenueGenerated: 155000,
    completedVisits: 405,
    experience: 18,
    avatarUrl: "/avatars/female_nurse.png",
    currentAssignment: {
      patientLocation: "مصر الجديدة - شارع الميرغني",
      eta: "وصلت بالفعل",
      service: "متابعة ورعاية ما بعد العمليات الجراحية",
    },
    recentActivity: [
      { id: "ECT1", date: "2024-05-18 02:00 PM", action: "بدء شيفت رعاية ما بعد الجراحة", status: "success" },
      { id: "ECT2", date: "2024-05-16 06:00 PM", action: "إعطاء محاليل ومضادات حيوية", status: "success" },
      { id: "ECT3", date: "2024-05-15 10:00 AM", action: "تغيير غيارات الجراحة المعقمة", status: "success" },
      { id: "ECT4", date: "2024-05-12 05:00 PM", action: "تفريغ ومتابعة الدرنقة الجراحية", status: "success" },
      { id: "ECT5", date: "2024-05-10 11:00 AM", action: "تحديث السجل الطبي الحيوي ورفعه للنظام", status: "success" },
    ],
  },
  {
    id: "NUR-1006",
    name: "فني تمريض / محمود زكريا",
    specialization: "مرافقة طبية وتمريض شامل",
    status: "متاح للتوجيه",
    nationalId: "29304198765432",
    syndicateNumber: "NUR-99210",
    rating: 4.8,
    totalRevenueGenerated: 98000,
    completedVisits: 160,
    experience: 9,
    avatarUrl: "/avatars/male_nurse.png",
    recentActivity: [
      { id: "FCT1", date: "2024-05-17 08:00 AM", action: "مرافقة سيارة إسعاف بين المحافظات", status: "success" },
      { id: "FCT2", date: "2024-05-15 12:00 PM", action: "تنظيم جدول أدوية أسبوعي لمريض", status: "success" },
      { id: "FCT3", date: "2024-05-14 02:00 AM", action: "نداء استغاثة ليلي - تواجد فوري", status: "success" },
      { id: "FCT4", date: "2024-05-10 09:00 AM", action: "شكوى من تأخر الوصول 15 دقيقة", status: "warning" },
      { id: "FCT5", date: "2024-05-08 11:00 PM", action: "متابعة تغذية عن طريق الأنبوب المعدي", status: "success" },
    ],
  }
];
