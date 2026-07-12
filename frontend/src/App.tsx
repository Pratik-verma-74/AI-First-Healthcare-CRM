import React from 'react';
import { Provider } from 'react-redux';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { store } from './store';
import { Header } from './components/Header/Header';
import { DashboardLayout } from './components/Dashboard/DashboardLayout';
import './styles/theme.css';

export const App: React.FC = () => {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
          <Header />
          <Routes>
            <Route path="/" element={<DashboardLayout />} />
            <Route path="*" element={<DashboardLayout />} />
          </Routes>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                borderRadius: '10px',
                background: '#181d2b',
                color: '#f0f3f9',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }
            }}
          />
        </div>
      </BrowserRouter>
    </Provider>
  );
};

export default App;
