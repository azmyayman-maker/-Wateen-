import { getCookie, setCookie, deleteCookie } from './cookies';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface FetchOptions extends RequestInit {
  data?: any;
  params?: Record<string, string>;
  requireAuth?: boolean;
}

// Store a promise to handle concurrent refresh requests
let refreshPromise: Promise<string | null> | null = null;

/**
 * Helper to build query parameters
 */
const buildUrl = (endpoint: string, params?: Record<string, string>) => {
  const url = new URL(`${BASE_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, value);
      }
    });
  }
  return url.toString();
};

/**
 * Attempts to refresh the access token using the stored refresh token.
 */
const refreshAccessToken = async (): Promise<string | null> => {
  // We only attempt to auto-refresh tokens on the client-side.
  // In Next.js Server Components, we cannot easily write new cookies to the response natively.
  if (typeof window === 'undefined') {
    return null;
  }

  const refreshToken = getCookie('refresh_token');
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${BASE_URL}/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Refresh failed');
    }

    const data = await response.json();
    setCookie('access_token', data.access, 1 / 96); // 15 mins
    
    // Some backends might return a new refresh token as well
    if (data.refresh) {
      setCookie('refresh_token', data.refresh, 7); // 7 days
    }
    
    return data.access;
  } catch (error) {
    // If refresh fails, clear tokens
    deleteCookie('access_token');
    deleteCookie('refresh_token');
    return null;
  }
};

/**
 * The core API Client wrapper replacing Axios
 */
export const apiClient = async <T>(endpoint: string, options: FetchOptions = {}): Promise<T> => {
  const { data, params, requireAuth = true, headers: customHeaders, ...customConfig } = options;

  let accessToken = getCookie('access_token');

  // Request Interceptor Logic
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...customHeaders,
  };

  if (requireAuth && accessToken) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken}`;
  }

  const config: RequestInit = {
    method: data ? 'POST' : 'GET',
    ...customConfig,
    headers,
  };

  if (data) {
    config.body = JSON.stringify(data);
  }

  const url = buildUrl(endpoint, params);

  // Initial Request
  let response = await fetch(url, config);

  // Response Interceptor Logic (Handling 401s for Auto-Refresh)
  if (response.status === 401 && requireAuth) {
    const refreshToken = getCookie('refresh_token');
    
    // If we have a refresh token, let's try to renew the access token
    if (refreshToken) {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }

      const newAccessToken = await refreshPromise;

      if (newAccessToken) {
        // Retry the original request with the new access token
        (headers as Record<string, string>)['Authorization'] = `Bearer ${newAccessToken}`;
        config.headers = headers;
        response = await fetch(url, config);
      } else {
        // Refresh failed, user is logged out. Redirect to login or dispatch event.
        if (typeof window !== 'undefined') {
           // We can throw a custom error to be caught by an ErrorBoundary or Provider
           throw new Error('SessionExpired');
        }
      }
    }
  }

  // Handle Response Output
  if (!response.ok) {
    // Attempt to parse standard backend error payloads
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { detail: response.statusText };
    }
    const error = new Error(errorData.detail || 'API Error');
    (error as any).status = response.status;
    (error as any).data = errorData;
    throw error;
  }

  // Handle empty responses (like 204 No Content)
  if (response.status === 204) {
    return {} as T;
  }

  return await response.json();
};
