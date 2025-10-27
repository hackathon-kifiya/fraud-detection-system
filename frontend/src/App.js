import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
  Link,
  useNavigate,
} from "react-router-dom";
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
  Badge,
  Collapse,
  Menu,
  MenuItem,
  Divider,
  CircularProgress,
} from "@mui/material";
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
  Logout as LogoutIcon,
  Person as PersonIcon,
  ExitToApp as ExitIcon,
  Assignment,
  Assignment as CaseManagementIcon,
  Storage as RuleManagementIcon,
  Speed as RuleTestIcon,
  Category as DataTypeManagementIcon,
  Assessment as TestEvaluationIcon,
  AutoAwesome as PlaygroundIcon,
  VerifiedUser as AuditorManagementIcon,
  Webhook as IntegrationSettingsIcon,
} from "@mui/icons-material";
import Dashboard from "./components/Dashboard";
import AuditorDashboard from "./components/AuditorDashboard";
import MyCasesPage from "./components/MyCasesPage";
import TransactionsPage from "./components/TransactionsPage";
import LoanRequestsPage from "./components/LoanRequestsPage";
import CreditHistoryPage from "./components/CreditHistoryPage";
import KycPage from "./components/KycPage";
import RepaymentsPage from "./components/RepaymentsPage";
import SettingsPage from "./components/SettingsPage";
import LoginPage from "./components/LoginPage";
import UserManagementPage from "./components/UserManagementPage";
import AuditorManagementPage from "./components/AuditorManagementPage";
import IntegrationSettingsPage from "./components/IntegrationSettingsPage";
import CaseManagementPage from "./components/CaseManagementPage";
import RuleManagementPage from "./components/RuleManagementPage";
import DataTypeManagementPage from "./components/DataTypeManagementPage";
import DataEvaluationPanel from "./components/DataEvaluationPanel";
import RiskDecisionPage from "./components/RiskDecisionPage";
import ProfilePage from "./components/ProfilePage";
import { AuthProvider, useAuth } from "./contexts/AuthContext";

const drawerWidth = 280;

function MainContent() {
  const location = useLocation();

  // Helper function to check if a route is active
  const isActiveRoute = (path) => {
    // Handle root path redirect to dashboard
    if (
      path === "/dashboard" &&
      (location.pathname === "/" || location.pathname === "/dashboard")
    ) {
      return true;
    }
    return location.pathname === path;
  };

  return <AppContent isActiveRoute={isActiveRoute} />;
}

function AppContent({ isActiveRoute }) {
  const { user, logout, isAuthenticated, login, loading } = useAuth();
  const navigate = useNavigate();
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "info",
  });
  const [openMenus, setOpenMenus] = useState({
    fraudDetection: true,
    ruleEngine: true,
    anomalyDetectionEngine: true,
    playground: false,
  });
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);

  const showSnackbar = (message, severity = "info") => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleUserMenuClick = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = () => {
    setUserMenuAnchor(null);
    logout();
  };

  const toggleMenu = (menu) => {
    setOpenMenus((prev) => ({
      ...prev,
      [menu]: !prev[menu],
    }));
  };

  // Get navigation items based on user role
  const getNavigationItems = () => {
    const role = user?.role;

    if (role === "superadmin") {
      return [
        {
          key: "dashboard",
          label: "Dashboard",
          icon: DashboardIcon,
          path: "/dashboard",
        },
        {
          key: "auditor-management",
          label: "Auditor Management",
          icon: AuditorManagementIcon,
          path: "/auditors",
        },
        {
          key: "data-type-management",
          label: "Data Management",
          icon: DataTypeManagementIcon,
          path: "/data-types",
        },
        {
          key: "rule-engine",
          label: "Rule Management",
          icon: RuleManagementIcon,
          path: "/rules",
        },
        {
          key: "risk-decision",
          label: "Risk Decision",
          icon: SecurityIcon,
          path: "/risk-decision",
        },
        {
          key: "playground",
          label: "Playground",
          icon: PlaygroundIcon,
          path: null,
          subItems: [
            {
              key: "rule-test-evaluation",
              label: "Rule Engine Test Evaluation",
              icon: RuleTestIcon,
              path: "/rules/evaluate",
            },
            {
              key: "anomaly-test-evaluation",
              label: "Anomaly Detection Test Evaluation",
              icon: TestEvaluationIcon,
              path: "/anomaly-detection/evaluate",
            },
            {
              key: "predictive-modeling-test-evaluation",
              label: "Predictive Modeling Test Evaluation",
              icon: TestEvaluationIcon,
              path: "/predictive-modeling/evaluate",
            },
          ],
        },
        {
          key: "users",
          label: "User Management",
          icon: GroupIcon,
          path: "/users",
        },
        {
          key: "integration-settings",
          label: "Integration",
          icon: IntegrationSettingsIcon,
          path: "/integration-settings",
        },
        {
          key: "settings",
          label: "Settings",
          icon: SettingsIcon,
          path: "/settings",
        },
      ];
    } else if (role === "admin") {
      return [
        {
          key: "dashboard",
          label: "Dashboard",
          icon: DashboardIcon,
          path: "/dashboard",
        },
        {
          key: "case-management",
          label: "Case Management",
          icon: CaseManagementIcon,
          path: "/case-management",
        },
        {
          key: "auditor-management",
          label: "Auditor Management",
          icon: AuditorManagementIcon,
          path: "/auditors",
        },
        {
          key: "data-type-management",
          label: "Data Management",
          icon: DataTypeManagementIcon,
          path: "/data-types",
        },
        {
          key: "rule-engine",
          label: "Rule Management",
          icon: RuleManagementIcon,
          path: "/rules",
        },
        {
          key: "risk-decision",
          label: "Risk Decision",
          icon: SecurityIcon,
          path: "/risk-decision",
        },
        {
          key: "playground",
          label: "Playground",
          icon: PlaygroundIcon,
          path: null,
          subItems: [
            {
              key: "rule-test-evaluation",
              label: "Rule Engine Test Evaluation",
              icon: RuleTestIcon,
              path: "/rules/evaluate",
            },
            {
              key: "anomaly-test-evaluation",
              label: "Anomaly Detection Test Evaluation",
              icon: TestEvaluationIcon,
              path: "/anomaly-detection/evaluate",
            },
            {
              key: "predictive-modeling-test-evaluation",
              label: "Predictive Modeling Test Evaluation",
              icon: TestEvaluationIcon,
              path: "/predictive-modeling/evaluate",
            },
          ],
        },
        {
          key: "users",
          label: "User Management",
          icon: GroupIcon,
          path: "/users",
        },
        {
          key: "integration-settings",
          label: "Integration",
          icon: IntegrationSettingsIcon,
          path: "/integration-settings",
        },
        {
          key: "settings",
          label: "Settings",
          icon: SettingsIcon,
          path: "/settings",
        },
      ];
    } else if (role === "analyst") {
      return [
        {
          key: "dashboard",
          label: "Dashboard",
          icon: DashboardIcon,
          path: "/dashboard",
        },
        {
          key: "my-cases",
          label: "My Cases",
          icon: Assignment,
          path: "/my-cases",
        },
        {
          key: "settings",
          label: "Settings",
          icon: SettingsIcon,
          path: "/settings",
        },
      ];
    } else {
      // Default for viewer or other roles
      return [
        {
          key: "dashboard",
          label: "Dashboard",
          icon: DashboardIcon,
          path: "/dashboard",
        },
        {
          key: "settings",
          label: "Settings",
          icon: SettingsIcon,
          path: "/settings",
        },
      ];
    }
  };

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
          bgcolor: "#f5f5f5",
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (!isAuthenticated()) {
    return <LoginPage onLogin={(user) => { login(user); navigate('/dashboard'); }} />;
  }

  return (
    <>
      <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "#f5f5f5" }}>
        {/* Sidebar */}
        <Drawer
          variant='permanent'
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            "& .MuiDrawer-paper": {
              width: drawerWidth,
              boxSizing: "border-box",
              bgcolor: "#023737",
              color: "white",
            },
          }}
        >
          <Box sx={{ p: 3, borderBottom: "1px solid #616161" }}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <img
                src='/logo.svg'
                alt='MAX Logo'
                style={{ width: 48, height: 48, marginRight: 8 }}
              />
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "baseline",
                    gap: 1,
                    mb: 0.5,
                  }}
                >
                  <Typography
                    variant='h5'
                    sx={{
                      fontWeight: "bold",
                      color: "white",
                      lineHeight: 1,
                      fontSize: "1.5rem",
                    }}
                  >
                    MAX
                  </Typography>
                  <Typography
                    variant='body2'
                    sx={{
                      color: "#bdbdbd",
                      fontWeight: "medium",
                      fontSize: "0.8rem",
                    }}
                  >
                    v0.1.0
                  </Typography>
                </Box>
                <Typography
                  variant='body2'
                  sx={{
                    color: "#bdbdbd",
                    fontSize: "0.75rem",
                    lineHeight: 1,
                    fontWeight: "normal",
                  }}
                >
                  Fraud Detection System
                </Typography>
              </Box>
            </Box>
          </Box>

          <Box sx={{ flexGrow: 1, pt: 2 }}>
            {/* Role-based Navigation */}
            <List sx={{ px: 1 }}>
              {getNavigationItems().map((item) => {
                const IconComponent = item.icon;

                if (item.subItems) {
                  // Item with submenu (like Fraud Detection for analysts)
                  return (
                    <Box key={item.key} sx={{ mb: 1 }}>
                      <ListItemButton
                        onClick={() => toggleMenu(item.key)}
                        sx={{
                          borderRadius: 1,
                          mx: 1,
                          mb: 1,
                          py: 1.5,
                          "&:hover": { bgcolor: "#616161" },
                        }}
                      >
                        <ListItemIcon
                          sx={{
                            color: "white",
                            minWidth: 40,
                            display: "flex",
                            alignItems: "center",
                          }}
                        >
                          <IconComponent sx={{ fontSize: "1.25rem" }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={item.label}
                          sx={{
                            color: "white",
                            "& .MuiListItemText-primary": {
                              fontSize: "0.9rem",
                              fontWeight: "600",
                              lineHeight: 1.2,
                            },
                          }}
                        />
                        {openMenus[item.key] ? (
                          <ExpandLess sx={{ fontSize: "1.25rem" }} />
                        ) : (
                          <ExpandMore sx={{ fontSize: "1.25rem" }} />
                        )}
                      </ListItemButton>

                      <Collapse
                        in={openMenus[item.key]}
                        timeout='auto'
                        unmountOnExit
                      >
                        <List component='div' disablePadding sx={{ px: 1 }}>
                          {item.subItems.map((subItem) => {
                            const SubIconComponent = subItem.icon;
                            return (
                              <ListItem
                                key={subItem.key}
                                disablePadding
                                sx={{ mb: 0.5 }}
                              >
                                <ListItemButton
                                  component={Link}
                                  to={subItem.path}
                                  sx={{
                                    borderRadius: 1,
                                    ml: 2,
                                    py: 1.25,
                                    bgcolor: isActiveRoute(subItem.path)
                                      ? "#ff9800"
                                      : "transparent",
                                    "&:hover": {
                                      bgcolor: isActiveRoute(subItem.path)
                                        ? "#ff9800"
                                        : "#616161",
                                    },
                                  }}
                                >
                                  <ListItemIcon
                                    sx={{
                                      color: "white",
                                      minWidth: 40,
                                      display: "flex",
                                      alignItems: "center",
                                    }}
                                  >
                                    <SubIconComponent
                                      sx={{ fontSize: "1.1rem" }}
                                    />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={subItem.label}
                                    sx={{
                                      color: "white",
                                      "& .MuiListItemText-primary": {
                                        fontSize: "0.85rem",
                                        fontWeight: "500",
                                        lineHeight: 1.2,
                                      },
                                    }}
                                  />
                                </ListItemButton>
                              </ListItem>
                            );
                          })}
                        </List>
                      </Collapse>
                    </Box>
                  );
                } else {
                  // Regular navigation item
                  return (
                    <ListItem key={item.key} disablePadding sx={{ mb: 0.5 }}>
                      <ListItemButton
                        component={Link}
                        to={item.path}
                        sx={{
                          borderRadius: 1,
                          mx: 1,
                          py: 1.5,
                          bgcolor: isActiveRoute(item.path)
                            ? "#ff9800"
                            : "transparent",
                          "&:hover": {
                            bgcolor: isActiveRoute(item.path)
                              ? "#ff9800"
                              : "#616161",
                          },
                        }}
                      >
                        <ListItemIcon
                          sx={{
                            color: "white",
                            minWidth: 40,
                            display: "flex",
                            alignItems: "center",
                          }}
                        >
                          <IconComponent sx={{ fontSize: "1.25rem" }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={item.label}
                          sx={{
                            color: "white",
                            "& .MuiListItemText-primary": {
                              fontSize: "0.9rem",
                              fontWeight: "600",
                              lineHeight: 1.2,
                            },
                          }}
                        />
                      </ListItemButton>
                    </ListItem>
                  );
                }
              })}
            </List>
          </Box>

          {/* Logout Button at Bottom */}
          <Box sx={{ p: 2, borderTop: "1px solid #616161" }}>
            <ListItem disablePadding>
              <ListItemButton
                onClick={handleLogout}
                sx={{
                  borderRadius: 1,
                  py: 1.5,
                  "&:hover": { bgcolor: "#616161" },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: "white",
                    minWidth: 40,
                    display: "flex",
                    alignItems: "center",
                  }}
                >
                  <ExitIcon sx={{ fontSize: "1.25rem" }} />
                </ListItemIcon>
                <ListItemText
                  primary='Logout'
                  sx={{
                    color: "white",
                    "& .MuiListItemText-primary": {
                      fontSize: "0.9rem",
                      fontWeight: "600",
                      lineHeight: 1.2,
                    },
                  }}
                />
              </ListItemButton>
            </ListItem>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
          {/* Header */}
          <AppBar
            position='static'
            elevation={0}
            sx={{
              bgcolor: "white",
              borderBottom: "1px solid #e0e0e0",
              color: "black",
            }}
          >
            <Toolbar sx={{ justifyContent: "flex-end", minHeight: "64px" }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <IconButton color='inherit' sx={{ p: 1 }}>
                  <Badge badgeContent={0} color='error'>
                    <NotificationsIcon
                      sx={{ color: "black", fontSize: "1.25rem" }}
                    />
                  </Badge>
                </IconButton>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                  <AccountCircleIcon 
                    sx={{ 
                      fontSize: "2rem", 
                      color: "text.secondary"
                    }} 
                  />
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "flex-start",
                    }}
                  >
                    <Typography
                      variant='body2'
                      sx={{
                        fontWeight: "bold",
                        fontSize: "0.875rem",
                        lineHeight: 1.2,
                      }}
                    >
                      {user?.first_name} {user?.last_name}
                    </Typography>
                    <Typography
                      variant='caption'
                      sx={{
                        color: "text.secondary",
                        fontSize: "0.75rem",
                        lineHeight: 1.2,
                      }}
                    >
                      {user?.role?.toUpperCase()}
                    </Typography>
                  </Box>
                  <IconButton
                    size='small'
                    onClick={handleUserMenuClick}
                    aria-controls={userMenuAnchor ? "user-menu" : undefined}
                    aria-haspopup='true'
                    aria-expanded={userMenuAnchor ? "true" : undefined}
                    sx={{ p: 0.5 }}
                  >
                    <KeyboardArrowDownIcon
                      sx={{ color: "black", fontSize: "1.25rem" }}
                    />
                  </IconButton>
                </Box>
              </Box>
            </Toolbar>
          </AppBar>

          {/* Page Content */}
          <Box sx={{ flexGrow: 1, p: 3 }}>
            <Routes>
              <Route path='/' element={<Navigate to='/dashboard' replace />} />
              <Route
                path='/dashboard'
                element={
                  user?.role === 'analyst' ? (
                    <AuditorDashboard onShowSnackbar={showSnackbar} />
                  ) : (
                    <Dashboard onShowSnackbar={showSnackbar} />
                  )
                }
              />
              <Route
                path='/my-cases'
                element={<MyCasesPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/transactions'
                element={<TransactionsPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/loan-requests'
                element={<LoanRequestsPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/credit-history'
                element={<CreditHistoryPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/kyc'
                element={<KycPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/repayments'
                element={<RepaymentsPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/settings'
                element={<SettingsPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/users'
                element={<UserManagementPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/auditors'
                element={<AuditorManagementPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/case-management'
                element={<CaseManagementPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/rules'
                element={<RuleManagementPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/data-types'
                element={<DataTypeManagementPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/rules/evaluate'
                element={<DataEvaluationPanel onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/anomaly-detection/evaluate'
                element={<DataEvaluationPanel onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/predictive-modeling/evaluate'
                element={<DataEvaluationPanel onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/risk-decision'
                element={<RiskDecisionPage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/profile'
                element={<ProfilePage onShowSnackbar={showSnackbar} />}
              />
              <Route
                path='/integration-settings'
                element={<IntegrationSettingsPage onShowSnackbar={showSnackbar} />}
              />
            </Routes>
          </Box>
        </Box>

        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        >
          <Alert
            onClose={handleSnackbarClose}
            severity={snackbar.severity}
            sx={{ width: "100%" }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>

        {/* User Menu Dropdown */}
        <Menu
          id='user-menu'
          anchorEl={userMenuAnchor}
          open={Boolean(userMenuAnchor)}
          onClose={handleUserMenuClose}
          anchorOrigin={{
            vertical: "bottom",
            horizontal: "right",
          }}
          transformOrigin={{
            vertical: "top",
            horizontal: "right",
          }}
          PaperProps={{
            sx: {
              mt: 1,
              minWidth: 200,
              "& .MuiMenuItem-root": {
                px: 2,
                py: 1,
              },
            },
          }}
        >
          <MenuItem
            onClick={() => {
              handleUserMenuClose();
              navigate("/profile");
            }}
          >
            <PersonIcon sx={{ mr: 1, fontSize: 20 }} />
            Profile
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleLogout} sx={{ color: "error.main" }}>
            <LogoutIcon sx={{ mr: 1, fontSize: 20 }} />
            Logout
          </MenuItem>
        </Menu>
      </Box>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path='/*' element={<MainContent />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
