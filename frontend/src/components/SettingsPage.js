import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { healthAPI } from '../services/api';

const SettingsPage = ({ onShowSnackbar }) => {
  const [systemStatus, setSystemStatus] = useState({
    database: 'checking',
    engine: 'checking',
    backend: 'checking',
    overall: 'checking'
  });
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({
    autoRefresh: true,
    notifications: true,
    darkMode: false,
    detectionThreshold: 70,
    maxRecordsPerPage: 50,
    dataRetentionDays: 30
  });

  const loadSystemStatus = async () => {
    try {
      setLoading(true);
      const response = await healthAPI.check();
      setSystemStatus(response.data);
    } catch (error) {
      setSystemStatus({
        database: 'error',
        engine: 'error',
        backend: 'error',
        overall: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSettingChange = (setting, value) => {
    setSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  const handleSaveSettings = () => {
    // In a real implementation, this would save to backend
    onShowSnackbar('Settings saved successfully', 'success');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon sx={{ color: '#4caf50' }} />;
      case 'warning':
        return <WarningIcon sx={{ color: '#ff9800' }} />;
      case 'error':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      default:
        return <CircularProgress size={20} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#4caf50';
      case 'warning': return '#ff9800';
      case 'error': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'healthy': return 'Online';
      case 'warning': return 'Warning';
      case 'error': return 'Offline';
      default: return 'Checking...';
    }
  };

  useEffect(() => {
    loadSystemStatus();
  }, []);

  return (
    <Paper sx={{ borderRadius: 2, boxShadow: 1, overflow: 'hidden' }}>
      <Box sx={{ p: 3, borderBottom: '1px solid #e0e0e0' }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#424242', mb: 1 }}>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure system settings and monitor system health.
        </Typography>
      </Box>

      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* System Status */}
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 2, boxShadow: 1, height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <SecurityIcon sx={{ mr: 1, color: '#1976d2' }} />
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242' }}>
                    System Status
                  </Typography>
                  <Button
                    size="small"
                    startIcon={<RefreshIcon />}
                    onClick={loadSystemStatus}
                    disabled={loading}
                    sx={{ ml: 'auto' }}
                  >
                    Refresh
                  </Button>
                </Box>

                {loading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <StorageIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary="Database"
                        secondary="PostgreSQL connection status"
                      />
                      <ListItemIcon>
                        {getStatusIcon(systemStatus.database)}
                      </ListItemIcon>
                      <Chip
                        label={getStatusText(systemStatus.database)}
                        size="small"
                        sx={{
                          bgcolor: getStatusColor(systemStatus.database) + '20',
                          color: getStatusColor(systemStatus.database),
                          fontWeight: 'bold'
                        }}
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemIcon>
                        <SpeedIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary="Detection Engine"
                        secondary="Python fraud detection service"
                      />
                      <ListItemIcon>
                        {getStatusIcon(systemStatus.engine)}
                      </ListItemIcon>
                      <Chip
                        label={getStatusText(systemStatus.engine)}
                        size="small"
                        sx={{
                          bgcolor: getStatusColor(systemStatus.engine) + '20',
                          color: getStatusColor(systemStatus.engine),
                          fontWeight: 'bold'
                        }}
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemIcon>
                        <SettingsIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary="Backend API"
                        secondary="Golang API service"
                      />
                      <ListItemIcon>
                        {getStatusIcon(systemStatus.backend)}
                      </ListItemIcon>
                      <Chip
                        label={getStatusText(systemStatus.backend)}
                        size="small"
                        sx={{
                          bgcolor: getStatusColor(systemStatus.backend) + '20',
                          color: getStatusColor(systemStatus.backend),
                          fontWeight: 'bold'
                        }}
                      />
                    </ListItem>
                  </List>
                )}

                <Divider sx={{ my: 2 }} />

                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: getStatusColor(systemStatus.overall), fontWeight: 'bold' }}>
                    Overall Status: {getStatusText(systemStatus.overall)}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={systemStatus.overall === 'healthy' ? 100 : systemStatus.overall === 'warning' ? 60 : 0}
                    sx={{ 
                      mt: 1, 
                      height: 8, 
                      borderRadius: 4,
                      bgcolor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: getStatusColor(systemStatus.overall)
                      }
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Application Settings */}
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 2, boxShadow: 1, height: '100%' }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242', mb: 2 }}>
                  Application Settings
                </Typography>

                <Box sx={{ mb: 3 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.autoRefresh}
                        onChange={(e) => handleSettingChange('autoRefresh', e.target.checked)}
                      />
                    }
                    label="Auto-refresh data"
                  />
                  <Typography variant="caption" color="text.secondary" display="block">
                    Automatically refresh data every 30 seconds
                  </Typography>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications}
                        onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                      />
                    }
                    label="Enable notifications"
                  />
                  <Typography variant="caption" color="text.secondary" display="block">
                    Show notifications for system events
                  </Typography>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.darkMode}
                        onChange={(e) => handleSettingChange('darkMode', e.target.checked)}
                      />
                    }
                    label="Dark mode"
                  />
                  <Typography variant="caption" color="text.secondary" display="block">
                    Switch to dark theme
                  </Typography>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Detection Threshold: {settings.detectionThreshold}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Minimum risk score to flag as suspicious
                  </Typography>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Max Records per Page: {settings.maxRecordsPerPage}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Maximum number of records to display per page
                  </Typography>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Data Retention: {settings.dataRetentionDays} days
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    How long to keep flagged items before archiving
                  </Typography>
                </Box>

                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveSettings}
                  fullWidth
                  sx={{ 
                    bgcolor: '#1976d2', 
                    '&:hover': { bgcolor: '#1565c0' },
                    borderRadius: 2,
                    py: 1.5
                  }}
                >
                  Save Settings
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* System Information */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242', mb: 2 }}>
            System Information
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                  v1.0.0
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Application Version
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                <Typography variant="h6" color="success" sx={{ fontWeight: 'bold' }}>
                  99.9%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Uptime
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                <Typography variant="h6" color="info" sx={{ fontWeight: 'bold' }}>
                  2.5GB
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Memory Usage
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                <Typography variant="h6" color="warning" sx={{ fontWeight: 'bold' }}>
                  15ms
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Response Time
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Paper>
  );
};

export default SettingsPage;

