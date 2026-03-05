import * as React from 'react';
import { Edit, SimpleForm, TextInput, BooleanInput, ArrayInput, SimpleFormIterator } from 'react-admin';

export const NurseEdit = () => (
    <Edit>
        <SimpleForm>
            <TextInput source="id" disabled />
            <TextInput source="user.name" label="Name" required />
            <BooleanInput source="is_available" label="Available" />
            <ArrayInput source="specializations" label="Specializations">
                <SimpleFormIterator inline>
                    <TextInput source="" label="Specialization" />
                </SimpleFormIterator>
            </ArrayInput>
        </SimpleForm>
    </Edit>
);
