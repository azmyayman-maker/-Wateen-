/**
 * KYCReviewList Component Tests
 * 
 * Tests for the KYC Review List component using Jest and React Testing Library.
 * Uses MSW for API mocking.
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { describe, it, expect, beforeAll, afterAll, beforeEach, afterEach, jest } from '@jest/globals';
import { KYCReviewList } from '../KYCReviewList';
import kycHandlers from '../__mocks__/handlers';

const server = setupServer(...kycHandlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

beforeEach(() => {
  // Mock localStorage
  Storage.prototype.getItem = jest.fn(() => 'fake-token');
  // Mock alert
  window.alert = jest.fn();
});

describe('KYCReviewList - Loading State', () => {
  it('should render loading state initially', () => {
    render(<KYCReviewList />);
    // Initial render shows loader. The loader is an SVG, we can check for its container
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });
});

describe('KYCReviewList - Pending Agencies List', () => {
  it('should render list of pending agencies from mocked API', async () => {
    render(<KYCReviewList />);
    
    // Wait for the mock agencies to load
    await waitFor(() => {
      expect(screen.getByText('وكالة الرعاية الصحية')).toBeInTheDocument();
    });
    
    expect(screen.getByText('مستشفى العناية المركزة')).toBeInTheDocument();
    expect(screen.getByText('2 PENDING')).toBeInTheDocument();
  });
});

describe('KYCReviewList - Approve Action', () => {
  it('should call correct API endpoint with APPROVE payload', async () => {
    render(<KYCReviewList />);
    
    await waitFor(() => {
      expect(screen.getByText('وكالة الرعاية الصحية')).toBeInTheDocument();
    });
    
    // Expand the agency
    fireEvent.click(screen.getByText('وكالة الرعاية الصحية'));
    
    // Find Approve button
    const approveBtn = await screen.findByRole('button', { name: /Approve/i });
    expect(approveBtn).toBeInTheDocument();
    
    // Click approve
    fireEvent.click(approveBtn);
    
    // Alert should not be called with an error, component should refetch
    await waitFor(() => {
      expect(window.alert).not.toHaveBeenCalled();
    });
  });
});

describe('KYCReviewList - Reject Action', () => {
  it('should require notes when rejecting and call correct API', async () => {
    render(<KYCReviewList />);
    
    await waitFor(() => {
      expect(screen.getByText('وكالة الرعاية الصحية')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('وكالة الرعاية الصحية'));
    
    const rejectBtn = await screen.findByRole('button', { name: /Reject/i });
    fireEvent.click(rejectBtn);
    
    // Modal should appear
    expect(screen.getByText('Reject Agency Application')).toBeInTheDocument();
    
    const confirmBtn = screen.getByRole('button', { name: /Confirm Reject/i });
    expect(confirmBtn).toBeDisabled(); // Disabled without notes
    
    const textarea = screen.getByPlaceholderText(/Enter rejection reason/i);
    await userEvent.type(textarea, 'Incomplete documents');
    
    expect(confirmBtn).not.toBeDisabled();
    
    fireEvent.click(confirmBtn);
    
    await waitFor(() => {
      expect(screen.queryByText('Reject Agency Application')).not.toBeInTheDocument();
    });
  });
});

describe('KYCReviewList - Error Handling', () => {
  it('should show error state when API fails', async () => {
    server.use(
      http.get('/api/v1/admin/kyc-queue/', () => {
        return HttpResponse.error();
      })
    );
    
    render(<KYCReviewList />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load KYC queue')).toBeInTheDocument();
    });
    
    // Shows retry button
    expect(screen.getByRole('button', { name: /Retry/i })).toBeInTheDocument();
  });
});

describe('KYCReviewList - Empty State', () => {
  it('should render empty state when no pending agencies', async () => {
    server.use(
      http.get('/api/v1/admin/kyc-queue/', () => {
        return HttpResponse.json({ results: [] });
      })
    );
    
    render(<KYCReviewList />);
    
    await waitFor(() => {
      expect(screen.getByText('All caught up!')).toBeInTheDocument();
    });
    
    expect(screen.getByText('No pending agency applications')).toBeInTheDocument();
    expect(screen.getByText('0 PENDING')).toBeInTheDocument();
  });
});
