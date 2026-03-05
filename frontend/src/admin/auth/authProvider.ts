import { AuthProvider } from 'react-admin';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * JWT-based AuthProvider for the Wateen B2B Agency Dashboard.
 * Uses HttpOnly cookies for token transport (T008 security requirement).
 * 
 * Flow:
 *   1. Login: POST /api/v1/auth/login/ with national_id + password
 *   2. Backend sets HttpOnly cookie with JWT tokens
 *   3. All subsequent requests include credentials (cookies sent automatically)
 *   4. Logout: POST /api/v1/auth/logout/ clears the cookie
 */
export const authProvider: AuthProvider = {
    login: async ({ username, password }) => {
        const response = await fetch(`${API_URL}/v1/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ national_id: username, password }),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'بيانات الدخول غير صحيحة');
        }

        const data = await response.json();

        // Store minimal user info in localStorage for React Admin identity
        // (tokens stay in HttpOnly cookies — not accessible via JS)
        localStorage.setItem('wateen_user', JSON.stringify({
            id: data.user?.id,
            fullName: data.user?.first_name_ar 
                ? `${data.user.first_name_ar} ${data.user.last_name_ar}`.trim()
                : data.user?.national_id,
            role: data.user?.role,
            agency: data.user?.agency,
        }));

        return Promise.resolve();
    },

    logout: async () => {
        try {
            await fetch(`${API_URL}/v1/auth/logout/`, {
                method: 'POST',
                credentials: 'include',
            });
        } catch {
            // Ignore network errors during logout
        }
        localStorage.removeItem('wateen_user');
        return Promise.resolve();
    },

    checkAuth: async () => {
        // Verify the session is still valid by hitting the profile endpoint
        const response = await fetch(`${API_URL}/v1/profile/`, {
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('غير مصرح');
        }

        return Promise.resolve();
    },

    checkError: async (error) => {
        const status = error?.status || error?.response?.status;
        if (status === 401 || status === 403) {
            localStorage.removeItem('wateen_user');
            throw new Error('انتهت صلاحية الجلسة');
        }
        return Promise.resolve();
    },

    getIdentity: async () => {
        const stored = localStorage.getItem('wateen_user');
        if (!stored) {
            return Promise.reject();
        }
        const user = JSON.parse(stored);
        return {
            id: user.id,
            fullName: user.fullName || 'مدير الوكالة',
            avatar: undefined,
        };
    },

    getPermissions: async () => {
        const stored = localStorage.getItem('wateen_user');
        if (!stored) return Promise.resolve('');
        const user = JSON.parse(stored);
        return Promise.resolve(user.role || '');
    },
};
