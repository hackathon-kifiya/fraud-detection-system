import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from './contexts/AuthContext';
import LabLayout from './components/LabLayout';
import LoginPage from './components/LoginPage';
import SandboxPage from './components/SandboxPage';
import DataSynthesisPage from './components/DataSynthesisPage';
import ProtectedRoute from './components/ProtectedRoute';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={
              <ProtectedRoute>
                <LabLayout />
              </ProtectedRoute>
            }>
              <Route index element={<Navigate to="/sandbox" replace />} />
              <Route path="sandbox" element={<SandboxPage />} />
              <Route path="data-synthesis" element={<DataSynthesisPage />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
