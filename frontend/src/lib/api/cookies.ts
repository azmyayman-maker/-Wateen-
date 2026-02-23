/**
 * Client-side & Server-side Cookie Management Utility
 * Zero-dependency replacement for js-cookie, compatible with Next.js 14 App Router
 */

export const getCookie = (name: string): string | null => {
  if (typeof window === 'undefined') {
    // Server-side (Next.js App Router)
    try {
      const { cookies } = require('next/headers');
      const cookieStore = cookies();
      return cookieStore.get(name)?.value || null;
    } catch (error) {
      // Fallback for build time or unsupported environments
      return null;
    }
  }

  // Client-side
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  if (match) return decodeURIComponent(match[2]);
  return null;
};

export const setCookie = (name: string, value: string, days = 7) => {
  const date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = "expires=" + date.toUTCString();

  if (typeof window === 'undefined') {
    // Server-side (Server Actions or Route Handlers only)
    try {
      const { cookies } = require('next/headers');
      cookies().set({
        name,
        value,
        expires: date,
        path: '/',
        sameSite: 'lax',
      });
      return;
    } catch (error) {
      console.warn('setCookie can only be used in Server Actions or Route Handlers on the server.');
      return;
    }
  }

  // Client-side
  document.cookie = `${name}=${encodeURIComponent(value)};${expires};path=/;SameSite=Lax`;
};

export const deleteCookie = (name: string) => {
  if (typeof window === 'undefined') {
    // Server-side
    try {
      const { cookies } = require('next/headers');
      cookies().delete(name);
      return;
    } catch (error) {
      console.warn('deleteCookie can only be used in Server Actions or Route Handlers on the server.');
      return;
    }
  }

  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
};
