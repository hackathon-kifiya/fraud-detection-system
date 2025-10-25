import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
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
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  Settings as SettingsIcon,
  Group as GroupIcon,
  AccountBalance as TransactionsIcon,
  CreditCard as LoanRequestsIcon,
  Assessment as CreditHistoryIcon,
  Person as KycIcon,
  Payment as RepaymentsIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material';
import Dashboard from './components/Dashboard';
import TransactionsPage from './components/TransactionsPage';
import LoanRequestsPage from './components/LoanRequestsPage';
import CreditHistoryPage from './components/CreditHistoryPage';
import KycPage from './components/KycPage';
import RepaymentsPage from './components/RepaymentsPage';
import SettingsPage from './components/SettingsPage';
import LoginPage from './components/LoginPage';
import UserManagementPage from './components/UserManagementPage';
import { AuthProvider, useAuth } from './contexts/AuthContext';

const drawerWidth = 280;

function AppContent() {
  const { user, logout, isAuthenticated, login } = useAuth();
  const location = useLocation();
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [openMenus, setOpenMenus] = useState({
    fraudDetection: true,
  });
  const [logoutDialog, setLogoutDialog] = useState(false);

  // Helper function to check if a route is active
  const isActiveRoute = (path) => {
    // Handle root path redirect to dashboard
    if (path === '/dashboard' && (location.pathname === '/' || location.pathname === '/dashboard')) {
      return true;
    }
    return location.pathname === path;
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleLogoutClick = () => {
    setLogoutDialog(true);
  };

  const handleLogoutConfirm = () => {
    setLogoutDialog(false);
    logout();
  };

  const handleLogoutCancel = () => {
    setLogoutDialog(false);
  };

  const toggleMenu = (menu) => {
    setOpenMenus(prev => ({
      ...prev,
      [menu]: !prev[menu]
    }));
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
              <img 
                src="/logo.svg" 
                alt="MAX Logo" 
                style={{ width: 40, height: 40, marginRight: 8 }}
              />
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'white' }}>
                MAX
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: '#bdbdbd' }}>
              Fraud Detection System
            </Typography>
          </Box>
          
          <Box sx={{ flexGrow: 1, pt: 2 }}>
            {/* Overview Section */}
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
                    component={Link}
                    to="/dashboard"
                    sx={{
                      borderRadius: 1,
                      mx: 1,
                      bgcolor: isActiveRoute('/dashboard') ? '#ff9800' : 'transparent',
                      '&:hover': { 
                        bgcolor: isActiveRoute('/dashboard') ? '#ff9800' : '#616161' 
                      },
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

            {/* Fraud Detection Types Section */}
            <Box sx={{ mb: 3 }}>
              <ListItemButton
                onClick={() => toggleMenu('fraudDetection')}
                sx={{
                  borderRadius: 1,
                  mx: 1,
                  mb: 1,
                  '&:hover': { bgcolor: '#616161' },
                }}
              >
                <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                  <SecurityIcon />
                </ListItemIcon>
                <ListItemText 
                  primary="Fraud Detection" 
                  sx={{ 
                    color: 'white',
                    '& .MuiListItemText-primary': {
                      fontSize: '0.9rem',
                      fontWeight: 'bold'
                    }
                  }} 
                />
                {openMenus.fraudDetection ? <ExpandLess /> : <ExpandMore />}
              </ListItemButton>
              
              <Collapse in={openMenus.fraudDetection} timeout="auto" unmountOnExit>
                <List component="div" disablePadding sx={{ px: 1 }}>
                  <ListItem disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      component={Link}
                      to="/transactions"
                      sx={{
                        borderRadius: 1,
                        ml: 2,
                        bgcolor: isActiveRoute('/transactions') ? '#ff9800' : 'transparent',
                        '&:hover': { 
                          bgcolor: isActiveRoute('/transactions') ? '#ff9800' : '#616161' 
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                        <TransactionsIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Transactions" 
                        sx={{ 
                          color: 'white',
                          '& .MuiListItemText-primary': {
                            fontSize: '0.85rem',
                            fontWeight: '500'
                          }
                        }} 
                      />
                    </ListItemButton>
                  </ListItem>
                  
                  <ListItem disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      component={Link}
                      to="/loan-requests"
                      sx={{
                        borderRadius: 1,
                        ml: 2,
                        bgcolor: isActiveRoute('/loan-requests') ? '#ff9800' : 'transparent',
                        '&:hover': { 
                          bgcolor: isActiveRoute('/loan-requests') ? '#ff9800' : '#616161' 
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                        <LoanRequestsIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Loan Requests" 
                        sx={{ 
                          color: 'white',
                          '& .MuiListItemText-primary': {
                            fontSize: '0.85rem',
                            fontWeight: '500'
                          }
                        }} 
                      />
                    </ListItemButton>
                  </ListItem>
                  
                  <ListItem disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      component={Link}
                      to="/credit-history"
                      sx={{
                        borderRadius: 1,
                        ml: 2,
                        bgcolor: isActiveRoute('/credit-history') ? '#ff9800' : 'transparent',
                        '&:hover': { 
                          bgcolor: isActiveRoute('/credit-history') ? '#ff9800' : '#616161' 
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                        <CreditHistoryIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Credit History" 
                        sx={{ 
                          color: 'white',
                          '& .MuiListItemText-primary': {
                            fontSize: '0.85rem',
                            fontWeight: '500'
                          }
                        }} 
                      />
                    </ListItemButton>
                  </ListItem>
                  
                  <ListItem disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      component={Link}
                      to="/kyc"
                      sx={{
                        borderRadius: 1,
                        ml: 2,
                        bgcolor: isActiveRoute('/kyc') ? '#ff9800' : 'transparent',
                        '&:hover': { 
                          bgcolor: isActiveRoute('/kyc') ? '#ff9800' : '#616161' 
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                        <KycIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="KYC Data" 
                        sx={{ 
                          color: 'white',
                          '& .MuiListItemText-primary': {
                            fontSize: '0.85rem',
                            fontWeight: '500'
                          }
                        }} 
                      />
                    </ListItemButton>
                  </ListItem>
                  
                  <ListItem disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      component={Link}
                      to="/repayments"
                      sx={{
                        borderRadius: 1,
                        ml: 2,
                        bgcolor: isActiveRoute('/repayments') ? '#ff9800' : 'transparent',
                        '&:hover': { 
                          bgcolor: isActiveRoute('/repayments') ? '#ff9800' : '#616161' 
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                        <RepaymentsIcon />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Repayments" 
                        sx={{ 
                          color: 'white',
                          '& .MuiListItemText-primary': {
                            fontSize: '0.85rem',
                            fontWeight: '500'
                          }
                        }} 
                      />
                    </ListItemButton>
                  </ListItem>
                </List>
          </Collapse>
        </Box>


        {/* User Management Section - Admin only */}
        {user?.role === 'admin' && (
          <Box sx={{ mb: 3 }}>
            <ListItem disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                component={Link}
                to="/users"
                sx={{
                  borderRadius: 1,
                  mx: 1,
                  bgcolor: isActiveRoute('/users') ? '#ff9800' : 'transparent',
                  '&:hover': { 
                    bgcolor: isActiveRoute('/users') ? '#ff9800' : '#616161' 
                  },
                }}
              >
                <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                  <GroupIcon />
                </ListItemIcon>
                <ListItemText 
                  primary="User Management" 
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
          </Box>
        )}

        {/* Settings Section */}
        <Box sx={{ mb: 3 }}>
          <ListItem disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              component={Link}
              to="/settings"
              sx={{
                borderRadius: 1,
                mx: 1,
                bgcolor: isActiveRoute('/settings') ? '#ff9800' : 'transparent',
                '&:hover': { 
                  bgcolor: isActiveRoute('/settings') ? '#ff9800' : '#616161' 
                },
              }}
            >
              <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Settings" 
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
              <Box sx={{ display: 'flex', alignItems: 'flex-end' }}>
                <img 
                  src="/logo.svg" 
                  alt="MAX Logo" 
                  style={{ width: 36, height: 36, marginRight: 6 }}
                />
                <Typography variant="h6" sx={{ color: 'black', fontWeight: 'bold' }}>
                  MAX
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <IconButton color="inherit">
                  <Badge badgeContent={0} color="error">
                    <NotificationsIcon sx={{ color: 'black' }} />
                  </Badge>
                </IconButton>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Avatar sx={{ width: 32, height: 32, bgcolor: '#ff9800' }}>
                    <AccountCircleIcon />
                  </Avatar>
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      {user?.first_name} {user?.last_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {user?.role?.toUpperCase()}
                    </Typography>
                  </Box>
                  <IconButton size="small" onClick={handleLogoutClick}>
                    <KeyboardArrowDownIcon sx={{ color: 'black' }} />
                  </IconButton>
                </Box>
              </Box>
            </Toolbar>
          </AppBar>

          {/* Page Content */}
          <Box sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route 
            path="/dashboard" 
            element={<Dashboard onShowSnackbar={showSnackbar} />} 
          />
          <Route 
            path="/transactions" 
            element={<TransactionsPage onShowSnackbar={showSnackbar} />} 
          />
          <Route 
            path="/loan-requests" 
            element={<LoanRequestsPage onShowSnackbar={showSnackbar} />} 
          />
          <Route 
            path="/credit-history" 
            element={<CreditHistoryPage onShowSnackbar={showSnackbar} />} 
          />
          <Route 
            path="/kyc" 
            element={<KycPage onShowSnackbar={showSnackbar} />} 
          />
          <Route 
            path="/repayments" 
            element={<RepaymentsPage onShowSnackbar={showSnackbar} />} 
          />
          <Route 
            path="/settings" 
            element={<SettingsPage onShowSnackbar={showSnackbar} />} 
          />
          <Route 
            path="/users" 
            element={<UserManagementPage onShowSnackbar={showSnackbar} />} 
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

        {/* Logout Confirmation Dialog */}
        <Dialog
          open={logoutDialog}
          onClose={handleLogoutCancel}
          aria-labelledby="logout-dialog-title"
          aria-describedby="logout-dialog-description"
        >
          <DialogTitle id="logout-dialog-title">
            Confirm Logout
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="logout-dialog-description">
              Are you sure you want to logout? You will need to sign in again to access the system.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleLogoutCancel} color="primary">
              Cancel
            </Button>
            <Button onClick={handleLogoutConfirm} color="error" variant="contained">
              Logout
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
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
