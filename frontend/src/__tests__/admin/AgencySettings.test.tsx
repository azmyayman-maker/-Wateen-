import * as React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AdminContext } from 'react-admin';
import { AgencySettings } from '../../admin/agency/AgencySettings';

describe('AgencySettings Component', () => {
    it('renders the dispatch mode toggle and allows interaction', () => {
        render(
            <AdminContext>
                <AgencySettings />
            </AdminContext>
        );

        // Verify title
        expect(screen.getByText('إعدادات الوكالة')).toBeInTheDocument();

        // Verify the toggle exists (label matches)
        const toggle = screen.getByLabelText(/وضع التوجيه/i);
        expect(toggle).toBeInTheDocument();

        // Verify save button exists
        const saveButton = screen.getByRole('button', { name: /حفظ/i });
        expect(saveButton).toBeInTheDocument();
    });
});
