/**
 * Nurse API Module
 * 
 * Provides typed functions for all nurse-side API operations.
 * Wraps the core apiClient with nurse-specific endpoints.
 */

import { apiClient } from './client';

// ─── Types ───────────────────────────────────────────────────────────────────

export interface NurseToggleRequest {
  is_online: boolean;
  latitude?: number | null;
  longitude?: number | null;
}

export interface NurseToggleResponse {
  is_online: boolean;
  message: string;
}

export interface PendingVisit {
  id: string;
  status: string;
  patient_name: string;
  service_name: string;
  latitude: number | null;
  longitude: number | null;
  distance_km: number | null;
  estimated_price: string;
  created_at: string;
}

export interface NurseRespondRequest {
  visit_id: string;
  action: 'accept' | 'decline';
}

export interface NurseRespondResponse {
  visit_id: string;
  status: string;
  message: string;
}

// ─── API Functions ───────────────────────────────────────────────────────────

/**
 * Toggle nurse online/offline availability.
 * When going online, latitude & longitude are required.
 */
export const toggleNurseAvailability = async (
  payload: NurseToggleRequest
): Promise<NurseToggleResponse> => {
  return apiClient<NurseToggleResponse>('/v1/visits/nurse/toggle/', {
    method: 'POST',
    data: payload,
  });
};

/**
 * Get pending visit requests for the nurse.
 * Returns visits with status=PENDING, ordered by most recent first.
 */
export const getPendingVisits = async (): Promise<PendingVisit[]> => {
  return apiClient<PendingVisit[]>('/v1/visits/nurse/pending/');
};

/**
 * Accept or decline a visit request.
 */
export const respondToVisit = async (
  payload: NurseRespondRequest
): Promise<NurseRespondResponse> => {
  return apiClient<NurseRespondResponse>('/v1/visits/nurse/respond/', {
    method: 'POST',
    data: payload,
  });
};
