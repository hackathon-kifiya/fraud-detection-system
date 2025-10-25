import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Alert,
  Snackbar,
  IconButton,
  Avatar,
  Badge,
} from '@mui/material';
import {
  Science as ScienceIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  PlayArrow as SandboxIcon,
  Storage as SynthesisIcon,
} from '@mui/icons-material';
import SandboxPage from './components/SandboxPage';
import DataSynthesisPage from './components/DataSynthesisPage';
import LoginPage from './components/LoginPage';
import { AuthProvider, useAuth } from './contexts/AuthContext';

const drawerWidth = 280;

function AppContent() {
  const { user, logout, isAuthenticated, login } = useAuth();
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  if (!isAuthenticated()) {
    return <LoginPage onLogin={login} />;
  }

  return (
    <Router>
      <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f5f5f5' }}>
        {/* Sidebar */}
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
              bgcolor: '#023737',
              color: 'white',
            },
          }}
        >
          <Box sx={{ p: 3, borderBottom: '1px solid #616161' }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-end', mb: 1 }}>
              <ScienceIcon sx={{ fontSize: 40, mr: 1, color: '#00e5ff' }} />
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'white' }}>
                LAB
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: '#bdbdbd' }}>
              Advanced Testing Portal
            </Typography>
          </Box>

          <Box sx={{ flexGrow: 1, pt: 2 }}>
            {/* Lab Tools Section */}
            <Box sx={{ mb: 3 }}>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: '#9e9e9e', 
                  px: 3, 
                  py: 1, 
                  display: 'block',
                  fontWeight: 'bold',
                  letterSpacing: '0.5px'
                }}
              >
                LAB TOOLS
              </Typography>
              <List sx={{ px: 1 }}>
                <ListItem disablePadding sx={{ mb: 0.5 }}>
                  <ListItemButton
                    component="a"
                    href="/sandbox"
                    sx={{
                      borderRadius: 1,
                      mx: 1,
                      '&:hover': { bgcolor: '#616161' },
                    }}
                  >
                    <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                      <SandboxIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Sandbox Testing" 
                      sx={{ 
                        color: 'white',
                        '& .MuiListItemText-primary': {
                          fontSize: '0.9rem',
                          fontWeight: 500
                        }
                      }} 
                    />
                  </ListItemButton>
                </ListItem>
                
                <ListItem disablePadding sx={{ mb: 0.5 }}>
                  <ListItemButton
                    component="a"
                    href="/data-synthesis"
                    sx={{
                      borderRadius: 1,
                      mx: 1,
                      '&:hover': { bgcolor: '#616161' },
                    }}
                  >
                    <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                      <SynthesisIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Data Synthesis" 
                      sx={{ 
                        color: 'white',
                        '& .MuiListItemText-primary': {
                          fontSize: '0.9rem',
                          fontWeight: 500
                        }
                      }} 
                    />
                  </ListItemButton>
                </ListItem>
              </List>
            </Box>
          </Box>

          {/* User Profile Section */}
          <Box sx={{ p: 2, borderTop: '1px solid #616161' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Avatar sx={{ bgcolor: '#ff9800', color: 'white', mr: 2 }}>
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </Avatar>
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="body2" sx={{ color: 'white', fontWeight: 'bold' }}>
                  {user?.first_name} {user?.last_name}
                </Typography>
                <Typography variant="caption" sx={{ color: '#bdbdbd' }}>
                  {user?.role?.replace('_', ' ').toUpperCase()}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton
                size="small"
                sx={{ color: 'white', bgcolor: '#616161', '&:hover': { bgcolor: '#757575' } }}
                onClick={logout}
              >
                <AccountCircleIcon />
              </IconButton>
            </Box>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Box component="main" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          {/* Top App Bar */}
          <AppBar position="static" elevation={0} sx={{ bgcolor: 'white', borderBottom: '1px solid #e0e0e0' }}>
            <Toolbar sx={{ justifyContent: 'space-between' }}>
              <Typography variant="h6" sx={{ color: '#023737', fontWeight: 'bold' }}>
                Lab Portal
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <IconButton color="inherit" sx={{ color: '#023737' }}>
                  <Badge badgeContent={0} color="error">
                    <NotificationsIcon />
                  </Badge>
                </IconButton>
              </Box>
            </Toolbar>
          </AppBar>

          {/* Page Content */}
          <Box sx={{ flexGrow: 1, p: 3 }}>
            <Routes>
              <Route index element={<Navigate to="/sandbox" replace />} />
              <Route 
                path="/sandbox" 
                element={<SandboxPage onShowSnackbar={showSnackbar} />} 
              />
              <Route 
                path="/data-synthesis" 
                element={<DataSynthesisPage onShowSnackbar={showSnackbar} />} 
              />
            </Routes>
          </Box>
        </Box>
      </Box>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
