import { apiClient } from './client';
import { setCookie, deleteCookie } from './cookies';

export interface AuthPair {
  access: string;
  refresh: string;
}

export interface RegisterResponse {
  user: {
    id: string;
    national_id: string;
    phone_number: string;
    role: string;
    first_name_ar: string;
    last_name_ar: string;
  };
  tokens: AuthPair;
}

export interface RegisterData {
  national_id: string;
  phone_number: string;
  password: string;
  role: 'PATIENT' | 'NURSE';
  first_name_ar?: string;
  last_name_ar?: string;
  email?: string;
}

/**
 * Decode JWT payload without external library.
 * Returns the payload object or null if decoding fails.
 */
function decodeJWTPayload(token: string): Record<string, any> | null {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

export const authAPI = {
  /**
   * Logs in a user returning access and refresh tokens.
   */
  login: async (credentials: any): Promise<AuthPair> => {
    const data = await apiClient<AuthPair>('/token/', {
      method: 'POST',
      data: credentials,
      requireAuth: false,
    });
    
    if (data.access && data.refresh) {
      setCookie('access_token', data.access, 1 / 96); 
      setCookie('refresh_token', data.refresh, 7);
    }
    
    return data;
  },

  /**
   * Registers a new user and stores JWT tokens automatically.
   */
  register: async (registerData: RegisterData): Promise<RegisterResponse> => {
    const data = await apiClient<RegisterResponse>('/register/', {
      method: 'POST',
      data: registerData,
      requireAuth: false,
    });

    // Auto-store tokens from registration response
    if (data.tokens?.access && data.tokens?.refresh) {
      setCookie('access_token', data.tokens.access, 1 / 96);
      setCookie('refresh_token', data.tokens.refresh, 7);
    }

    return data;
  },

  /**
   * Upload KYC document for nurse verification.
   * Requires authentication (JWT from login/register).
   */
  uploadKYCDocument: async (
    documentType: 'NATIONAL_ID' | 'SYNDICATE_CARD',
    file: File
  ): Promise<any> => {
    const formData = new FormData();
    formData.append('document_type', documentType);
    formData.append('document_file', file);

    const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    const { getCookie: getC } = await import('./cookies');
    const accessToken = getC('access_token');

    const response = await fetch(`${BASE_URL}/kyc/upload/`, {
      method: 'POST',
      headers: {
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: formData,
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }
      const error = new Error(errorData.detail || errorData.reason || 'Upload failed');
      (error as any).status = response.status;
      (error as any).data = errorData;
      throw error;
    }

    return await response.json();
  },

  /**
   * Clears tokens locally.
   */
  logout: () => {
    deleteCookie('access_token');
    deleteCookie('refresh_token');
  },
  
  /**
   * Validates the current token with the backend directly
   */
  verifyToken: async (token: string) => {
    return await apiClient('/token/verify/', {
      method: 'POST',
      data: { token },
      requireAuth: false,
    });
  },

  /**
   * Extracts user info from JWT token payload.
   */
  getUserFromToken: (token: string): { id: string; role: 'patient' | 'nurse' | 'admin'; agencyId?: string } | null => {
    const payload = decodeJWTPayload(token);
    if (!payload) return null;
    
    // SimpleJWT stores user_id in the payload
    const id = payload.user_id || payload.sub || '';
    const roleRaw = (payload.role || 'patient').toLowerCase();
    const role = (['patient', 'nurse', 'admin'].includes(roleRaw) ? roleRaw : 'patient') as 'patient' | 'nurse' | 'admin';
    const agencyId = payload.agency_id || payload.agencyId || undefined;
    
    return { id: String(id), role, agencyId: agencyId ? String(agencyId) : undefined };
  },
};
