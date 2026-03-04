import polyglotI18nProvider from 'ra-i18n-polyglot';
import { arabicMessages } from './ar';

const customArabicMessages = {
    ...arabicMessages,
    resources: {
        nurses: {
            name: "الممرضين",
            fields: {
                id: "المعرف",
                name: "الاسم",
                is_available: "متاح",
                specializations: "التخصصات"
            }
        }
    },
    custom: {
        agency_settings: {
            name: "إعدادات الوكالة",
            dispatch_mode: "وضع التوجيه",
            b2b_hours: "ساعات العمل"
        }
    }
};

export const i18nProvider = polyglotI18nProvider(
    () => customArabicMessages as any,
    'ar',
    [{ locale: 'ar', name: 'العربية' }]
);
