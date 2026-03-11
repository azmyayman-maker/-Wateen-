import React from 'react';
import { Admin, Resource, Layout } from 'react-admin';
import { VisitQueueList } from './pages/VisitQueue';

// Mock dataprovider for UI demonstration
const dataProvider = {
  getList: (resource: string, params: any) => Promise.resolve({ data: [], total: 0 }),
  getOne: () => Promise.resolve({ data: {} }),
  getMany: () => Promise.resolve({ data: [] }),
  getManyReference: () => Promise.resolve({ data: [], total: 0 }),
  update: () => Promise.resolve({ data: {} }),
  updateMany: () => Promise.resolve({ data: [] }),
  create: () => Promise.resolve({ data: {} }),
  delete: () => Promise.resolve({ data: {} }),
  deleteMany: () => Promise.resolve({ data: [] }),
};

const App = () => (
  <Admin dataProvider={dataProvider}>
    {/* Register the VisitQueueList component in the React Admin app configuration */}
    <Resource 
      name="visit-queue" 
      list={VisitQueueList} 
      options={{ label: "قائمة الانتظار" }} 
    />
  </Admin>
);

export default App;
