import * as React from 'react';
import { Admin, Resource, CustomRoutes } from 'react-admin';
import { Route } from 'react-router-dom';
import simpleRestProvider from 'ra-data-simple-rest';
import { fetchUtils } from 'ra-core';
import { theme } from './theme';
import { i18nProvider } from './i18n';
import { WateenLayout } from './layout/WateenLayout';
import { CommandCenter } from './dashboard/CommandCenter';
import { NurseList } from './nurses/NurseList';
import { NurseCreate } from './nurses/NurseCreate';
import { NurseEdit } from './nurses/NurseEdit';
import { AgencySettings } from './agency/AgencySettings';
import { OperationsCenter } from './agency/OperationsCenter';
import { GeographicalScope } from './agency/GeographicalScope';
import { FinancialLedger } from './agency/FinancialLedger';

// Use HttpOnly Cookies context for Data Provider (T008)
const fetchJson = (url: string, options: any = {}) => {
    options.user = {
        authenticated: true,
        token: 'HttpOnly' // In a real scenario, the token flows via HttpOnly cookie
    };
    options.credentials = 'include';
    return fetchUtils.fetchJson(url, options);
};

// Dummy provider for scaffolding phase or hook to Django REST
const dataProvider = simpleRestProvider('http://localhost:8000/api', fetchJson);

const App = () => (
    <Admin
        theme={theme}
        i18nProvider={i18nProvider}
        dataProvider={dataProvider}
        layout={WateenLayout}
        dashboard={CommandCenter}
        requireAuth={false}
    >
        <Resource
            name="nurses"
            list={NurseList}
            create={NurseCreate}
            edit={NurseEdit}
            options={{ label: 'الممرضين' }}
        />
        <CustomRoutes>
            <Route path="/coverage" element={<GeographicalScope />} />
            <Route path="/operations" element={<OperationsCenter />} />
            <Route path="/financials" element={<FinancialLedger />} />
            <Route path="/settings" element={<AgencySettings />} />
        </CustomRoutes>
    </Admin>
);

export default App;
