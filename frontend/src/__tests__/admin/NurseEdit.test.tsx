import * as React from 'react';
import { render, screen } from '@testing-library/react';
import { AdminContext, testDataProvider } from 'react-admin';
import { NurseEdit } from '../../admin/nurses/NurseEdit';

describe('NurseEdit Component', () => {
    it('renders the availability toggle and user details fields', async () => {
        const dataProvider = testDataProvider({
            getOne: () => Promise.resolve({ data: { id: 1, 'user.name': 'Omar', is_available: true, specializations: ['ICU'] } }) as any,
        });

        render(
            <AdminContext dataProvider={dataProvider}>
                <NurseEdit />
            </AdminContext>
        );

        // Wait for the form to load
        const nameInput = await screen.findByLabelText(/Name/i);
        expect(nameInput).toBeInTheDocument();

        // Check availability toggle
        const availabilityToggle = screen.getByLabelText(/Available/i);
        expect(availabilityToggle).toBeInTheDocument();
    });
});
