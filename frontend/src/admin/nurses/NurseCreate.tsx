import * as React from 'react';
import { Create, SimpleForm, TextInput, BooleanInput, ArrayInput, SimpleFormIterator } from 'react-admin';

export const NurseCreate = () => (
    <Create>
        <SimpleForm>
            <TextInput source="user.name" label="Name" required />
            <BooleanInput source="is_available" label="Available" defaultValue={true} />
            <ArrayInput source="specializations" label="Specializations">
                <SimpleFormIterator inline>
                    <TextInput source="" label="Specialization" />
                </SimpleFormIterator>
            </ArrayInput>
        </SimpleForm>
    </Create>
);
