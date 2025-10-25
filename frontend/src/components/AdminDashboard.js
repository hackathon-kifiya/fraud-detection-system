import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  People,
  Assignment,
  Settings,
  Refresh,
  Download,
  Visibility,
} from '@mui/icons-material';
import { adminAPI } from '../services/api';

const AdminDashboard = ({ onShowSnackbar }) => {
  const [kpiMetrics, setKpiMetrics] = useState(null);
  const [systemOverview, setSystemOverview] = useState(null);
  const [recentReports, setRecentReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [kpiResponse, overviewResponse, reportsResponse] = await Promise.all([
        adminAPI.getKPIMetrics(),
        adminAPI.getSystemOverview(),
        adminAPI.getPerformanceReports({ limit: 5 })
      ]);

      setKpiMetrics(kpiResponse.data.metrics);
      setSystemOverview(overviewResponse.data);
      setRecentReports(reportsResponse.data.reports || []);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
      onShowSnackbar('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const getKPIStatus = (value, threshold = 0.1) => {
    if (value <= threshold) return 'success';
    if (value <= threshold * 2) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={loadDashboardData}>
          Retry
        </Button>
      }>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Admin Dashboard
        </Typography>
        <Box>
          <Tooltip title="Refresh Data">
            <IconButton onClick={loadDashboardData} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* KPI Metrics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    False Positive Rate
                  </Typography>
                  <Typography variant="h4" component="div">
                    {formatPercentage(kpiMetrics?.false_positive_rate || 0)}
                  </Typography>
                </Box>
                <TrendingDown color={getKPIStatus(kpiMetrics?.false_positive_rate) === 'success' ? 'success' : 'error'} />
              </Box>
              <LinearProgress
                variant="determinate"
                value={(kpiMetrics?.false_positive_rate || 0) * 100}
                color={getKPIStatus(kpiMetrics?.false_positive_rate)}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    False Negative Rate
                  </Typography>
                  <Typography variant="h4" component="div">
                    {formatPercentage(kpiMetrics?.false_negative_rate || 0)}
                  </Typography>
                </Box>
                <TrendingDown color={getKPIStatus(kpiMetrics?.false_negative_rate) === 'success' ? 'success' : 'error'} />
              </Box>
              <LinearProgress
                variant="determinate"
                value={(kpiMetrics?.false_negative_rate || 0) * 100}
                color={getKPIStatus(kpiMetrics?.false_negative_rate)}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Model Accuracy
                  </Typography>
                  <Typography variant="h4" component="div">
                    {formatPercentage(kpiMetrics?.accuracy || 0)}
                  </Typography>
                </Box>
                <TrendingUp color={getKPIStatus(1 - kpiMetrics?.accuracy) === 'success' ? 'success' : 'error'} />
              </Box>
              <LinearProgress
                variant="determinate"
                value={(kpiMetrics?.accuracy || 0) * 100}
                color={getKPIStatus(1 - kpiMetrics?.accuracy)}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Throughput
                  </Typography>
                  <Typography variant="h4" component="div">
                    {kpiMetrics?.throughput || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    transactions/hour
                  </Typography>
                </Box>
                <Assessment color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Overview and Recent Reports */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Overview
              </Typography>
              {systemOverview ? (
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Total Transactions Processed
                    </Typography>
                    <Typography variant="h5">
                      {systemOverview.total_transactions?.toLocaleString() || 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Active Auditors
                    </Typography>
                    <Typography variant="h5">
                      {systemOverview.active_auditors || 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Pending Reviews
                    </Typography>
                    <Typography variant="h5">
                      {systemOverview.pending_reviews || 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      System Uptime
                    </Typography>
                    <Typography variant="h5">
                      {systemOverview.uptime || '99.9%'}
                    </Typography>
                  </Grid>
                </Grid>
              ) : (
                <Typography color="textSecondary">No data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Reports
              </Typography>
              {recentReports.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>Date</TableCell>
                        <TableCell>Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recentReports.map((report) => (
                        <TableRow key={report.id}>
                          <TableCell>
                            <Chip 
                              label={report.report_type} 
                              size="small" 
                              color="primary" 
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(report.generated_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <Tooltip title="View Report">
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Download">
                              <IconButton size="small">
                                <Download />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography color="textSecondary">No recent reports</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Box display="flex" gap={2} flexWrap="wrap">
          <Button
            variant="contained"
            startIcon={<Assessment />}
            onClick={() => {/* Navigate to reports */}}
          >
            Generate Report
          </Button>
          <Button
            variant="outlined"
            startIcon={<People />}
            onClick={() => {/* Navigate to auditor management */}}
          >
            Manage Auditors
          </Button>
          <Button
            variant="outlined"
            startIcon={<Assignment />}
            onClick={() => {/* Navigate to case assignments */}}
          >
            Assign Cases
          </Button>
          <Button
            variant="outlined"
            startIcon={<Settings />}
            onClick={() => {/* Navigate to system config */}}
          >
            System Settings
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default AdminDashboard;
