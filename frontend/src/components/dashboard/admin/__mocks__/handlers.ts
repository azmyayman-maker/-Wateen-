/**
 * MSW API Handlers for KYC Endpoints
 * 
 * Mock API handlers for testing the KYC Review UI components.
 * These handlers simulate the backend API responses.
 */

import { http, HttpResponse, delay } from 'msw';

// Mock data for pending KYC queue
const mockPendingAgencies = [
  {
    id: '550e8400-e29b-41d4-a716-446655440001',
    manager_name: 'وكالة الرعاية الصحية',
    commercial_registry: 'CR123456',
    moh_license_number: 'MOH456789',
    tax_id: 'TAX123456',
    status: 'pending',
    created_at: '2026-03-01T10:00:00Z',
    documents: [
      {
        id: 'doc-1',
        document_type: 'COMMERCIAL_REGISTRY',
        file: '/media/kyc/doc1.pdf',
        status: 'PENDING',
        uploaded_at: '2026-03-01T10:00:00Z',
      },
      {
        id: 'doc-2',
        document_type: 'MOH_LICENSE',
        file: '/media/kyc/doc2.pdf',
        status: 'PENDING',
        uploaded_at: '2026-03-01T10:00:00Z',
      },
      {
        id: 'doc-3',
        document_type: 'TAX_ID',
        file: '/media/kyc/doc3.pdf',
        status: 'PENDING',
        uploaded_at: '2026-03-01T10:00:00Z',
      },
    ],
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440002',
    manager_name: 'مستشفى العناية المركزة',
    commercial_registry: 'CR789012',
    moh_license_number: 'MOH456790',
    tax_id: 'TAX789012',
    status: 'pending',
    created_at: '2026-03-02T14:30:00Z',
    documents: [
      {
        id: 'doc-4',
        document_type: 'COMMERCIAL_REGISTRY',
        file: '/media/kyc/doc4.pdf',
        status: 'PENDING',
        uploaded_at: '2026-03-02T14:30:00Z',
      },
    ],
  },
];

// Mock audit logs
const mockAuditLogs = [
  {
    id: 'log-1',
    agency_id: '550e8400-e29b-41d4-a716-446655440001',
    reviewer: {
      id: 'admin-1',
      name: 'مسؤول النظام',
    },
    action: 'APPROVE',
    notes: 'تم التحقق من جميع المستندات',
    timestamp: '2026-03-01T12:00:00Z',
  },
];

export const kycHandlers = [
  // GET /api/v1/admin/kyc-queue/ - List pending agencies
  http.get('/api/v1/admin/kyc-queue/', async ({ request }) => {
    await delay(200);
    
    const url = new URL(request.url);
    const search = url.searchParams.get('search');
    
    let agencies = [...mockPendingAgencies];
    
    if (search) {
      agencies = agencies.filter(
        (a) =>
          a.manager_name.includes(search) ||
          a.commercial_registry.includes(search)
      );
    }
    
    return HttpResponse.json(agencies);
  }),

  // POST /api/v1/admin/agencies/:pk/review/ - Review agency KYC
  http.post('/api/v1/admin/agencies/:id/review/', async ({ params, request }: any) => {
    await delay(300);
    
    const body = await request.json() as { action: string; notes?: string };
    const { id } = params;
    
    // Find the agency
    const agencyIndex = mockPendingAgencies.findIndex(
      (a) => String(a.id) === String(id)
    );
    
    if (agencyIndex === -1) {
      return HttpResponse.json(
        { error: 'Agency not found' },
        { status: 404 }
      );
    }
    
    if (!body.action || !['APPROVE', 'REJECT'].includes(body.action)) {
      return HttpResponse.json(
        { error: 'Invalid action. Must be APPROVE or REJECT' },
        { status: 400 }
      );
    }
    
    if (body.action === 'REJECT' && (!body.notes || body.notes.trim() === '')) {
      return HttpResponse.json(
        { error: 'Notes are required when rejecting' },
        { status: 400 }
      );
    }
    
    // Create audit log entry
    const newLog = {
      id: `log-${Date.now()}`,
      agency_id: id,
      reviewer: {
        id: 'current-admin',
        name: 'مسؤول النظام',
      },
      action: body.action,
      notes: body.notes || '',
      timestamp: new Date().toISOString(),
    };
    
    mockAuditLogs.unshift(newLog);
    
    return HttpResponse.json({
      success: true,
      status: body.action === 'APPROVE' ? 'verified' : 'rejected',
      audit_log: newLog,
    });
  }),

  // GET /api/v1/admin/agencies/:id/kyc-audit-logs/ - Get audit logs
  http.get('/api/v1/admin/agencies/:id/kyc-audit-logs/', async ({ params }: any) => {
    await delay(200);
    
    const { id } = params;
    const logs = mockAuditLogs.filter((log) => log.agency_id === id);
    
    return HttpResponse.json(logs);
  }),
];

export default kycHandlers;
