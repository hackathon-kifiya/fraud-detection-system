import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
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
  Dashboard as DashboardIcon,
  Upload as UploadIcon,
  Analytics as AnalyticsIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  Flag as FlagIcon,
  Report as ReportIcon,
  Settings as SettingsIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import UploadPage from './components/UploadPage';
import Dashboard from './components/Dashboard';
import { healthAPI } from './services/api';

const drawerWidth = 280;

function App() {
  const [healthStatus, setHealthStatus] = useState('checking');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

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
              bgcolor: '#424242',
              color: 'white',
            },
          }}
        >
          <Box sx={{ p: 3, borderBottom: '1px solid #616161' }}>
            <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'white' }}>
              Fraud Detection
            </Typography>
            <Typography variant="body2" sx={{ color: '#bdbdbd' }}>
              Security System
            </Typography>
          </Box>
          
          <Box sx={{ flexGrow: 1, pt: 2 }}>
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
                OVERVIEW
              </Typography>
              <List sx={{ px: 1 }}>
                <ListItem disablePadding sx={{ mb: 0.5 }}>
                  <ListItemButton
                    sx={{
                      borderRadius: 1,
                      mx: 1,
                      bgcolor: '#ff9800',
                    }}
                  >
                    <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                      <DashboardIcon />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Dashboard" 
                      sx={{ 
                        color: 'white',
                        '& .MuiListItemText-primary': {
                          fontSize: '0.9rem',
                          fontWeight: 'bold'
                        }
                      }} 
                    />
                  </ListItemButton>
                </ListItem>
              </List>
            </Box>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          {/* Header */}
          <AppBar 
            position="static" 
            elevation={0}
            sx={{ 
              bgcolor: 'white', 
              borderBottom: '1px solid #e0e0e0',
              color: 'black'
            }}
          >
            <Toolbar sx={{ justifyContent: 'space-between' }}>
              <Typography variant="h6" sx={{ color: 'black', fontWeight: 'bold' }}>
                Fraud Detection System
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  Status: {healthStatus === 'healthy' ? '🟢' : '🔴'} {healthStatus}
                </Typography>
                <IconButton color="inherit">
                  <Badge badgeContent={0} color="error">
                    <NotificationsIcon sx={{ color: 'black' }} />
                  </Badge>
                </IconButton>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#ff9800' }}>
                  <AccountCircleIcon />
                </Avatar>
                <IconButton size="small">
                  <KeyboardArrowDownIcon sx={{ color: 'black' }} />
                </IconButton>
              </Box>
            </Toolbar>
          </AppBar>

          {/* Page Content */}
          <Box sx={{ flexGrow: 1, p: 3 }}>
            <Routes>
              <Route path="/" element={<Navigate to="/upload" replace />} />
              <Route 
                path="/upload" 
                element={<UploadPage onShowSnackbar={showSnackbar} />} 
              />
              <Route 
                path="/dashboard" 
                element={<Dashboard onShowSnackbar={showSnackbar} />} 
              />
            </Routes>
          </Box>
        </Box>

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
      </Box>
    </Router>
  );
}

export default App;
