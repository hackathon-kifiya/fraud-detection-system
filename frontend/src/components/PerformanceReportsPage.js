import React, { useState, useEffect } from 'react';
import {
  Box,
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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
  Tooltip,
  Menu,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add,
  Download,
  Visibility,
  MoreVert,
  Assessment,
  TrendingUp,
  DateRange,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { adminAPI } from '../services/api';

const PerformanceReportsPage = ({ onShowSnackbar }) => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [menuReport, setMenuReport] = useState(null);

  // Form state for creating new report
  const [reportForm, setReportForm] = useState({
    report_type: 'system_throughput',
    start_date: null,
    end_date: null,
  });

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await adminAPI.getPerformanceReports();
      setReports(response.data.reports || []);
    } catch (err) {
      console.error('Error loading reports:', err);
      setError('Failed to load reports');
      onShowSnackbar('Failed to load reports', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReport = async () => {
    try {
      if (!reportForm.start_date || !reportForm.end_date) {
        onShowSnackbar('Please select start and end dates', 'error');
        return;
      }

      const reportData = {
        ...reportForm,
        start_date: reportForm.start_date.toISOString().split('T')[0],
        end_date: reportForm.end_date.toISOString().split('T')[0],
      };

      await adminAPI.generatePerformanceReport(reportData);
      onShowSnackbar('Report generated successfully', 'success');
      setCreateDialogOpen(false);
      setReportForm({
        report_type: 'system_throughput',
        start_date: null,
        end_date: null,
      });
      loadReports();
    } catch (err) {
      console.error('Error creating report:', err);
      onShowSnackbar('Failed to create report', 'error');
    }
  };

  const handleViewReport = async (reportId) => {
    try {
      const response = await adminAPI.getPerformanceReport(reportId);
      setSelectedReport(response.data);
      setViewDialogOpen(true);
    } catch (err) {
      console.error('Error loading report details:', err);
      onShowSnackbar('Failed to load report details', 'error');
    }
  };

  const handleDownloadReport = async (reportId) => {
    try {
      // This would typically trigger a file download
      onShowSnackbar('Download started', 'info');
    } catch (err) {
      console.error('Error downloading report:', err);
      onShowSnackbar('Failed to download report', 'error');
    }
  };

  const handleDeleteReport = async (reportId) => {
    try {
      await adminAPI.deletePerformanceReport(reportId);
      onShowSnackbar('Report deleted successfully', 'success');
      loadReports();
    } catch (err) {
      console.error('Error deleting report:', err);
      onShowSnackbar('Failed to delete report', 'error');
    }
  };

  const handleMenuOpen = (event, report) => {
    setMenuAnchor(event.currentTarget);
    setMenuReport(report);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setMenuReport(null);
  };

  const getReportTypeColor = (type) => {
    const colors = {
      system_throughput: 'primary',
      auditor_performance: 'secondary',
      model_performance: 'success',
      time_analysis: 'warning',
      type_analysis: 'info',
    };
    return colors[type] || 'default';
  };

  const getReportTypeLabel = (type) => {
    const labels = {
      system_throughput: 'System Throughput',
      auditor_performance: 'Auditor Performance',
      model_performance: 'Model Performance',
      time_analysis: 'Time Analysis',
      type_analysis: 'Type Analysis',
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Performance Reports
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Generate Report
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Report Type</TableCell>
                    <TableCell>Period</TableCell>
                    <TableCell>Generated By</TableCell>
                    <TableCell>Generated At</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reports.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell>
                        <Chip
                          label={getReportTypeLabel(report.report_type)}
                          color={getReportTypeColor(report.report_type)}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(report.start_date).toLocaleDateString()} - {new Date(report.end_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{report.generated_by}</TableCell>
                      <TableCell>
                        {new Date(report.generated_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label="Completed"
                          color="success"
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Report">
                          <IconButton
                            size="small"
                            onClick={() => handleViewReport(report.id)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download">
                          <IconButton
                            size="small"
                            onClick={() => handleDownloadReport(report.id)}
                          >
                            <Download />
                          </IconButton>
                        </Tooltip>
                        <IconButton
                          size="small"
                          onClick={(e) => handleMenuOpen(e, report)}
                        >
                          <MoreVert />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Create Report Dialog */}
        <Dialog
          open={createDialogOpen}
          onClose={() => setCreateDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Generate Performance Report</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Report Type</InputLabel>
                  <Select
                    value={reportForm.report_type}
                    onChange={(e) => setReportForm({ ...reportForm, report_type: e.target.value })}
                    label="Report Type"
                  >
                    <MenuItem value="system_throughput">System Throughput</MenuItem>
                    <MenuItem value="auditor_performance">Auditor Performance</MenuItem>
                    <MenuItem value="model_performance">Model Performance</MenuItem>
                    <MenuItem value="time_analysis">Time Analysis</MenuItem>
                    <MenuItem value="type_analysis">Type Analysis</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <DatePicker
                  label="Start Date"
                  value={reportForm.start_date}
                  onChange={(date) => setReportForm({ ...reportForm, start_date: date })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
              <Grid item xs={6}>
                <DatePicker
                  label="End Date"
                  value={reportForm.end_date}
                  onChange={(date) => setReportForm({ ...reportForm, end_date: date })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleCreateReport} variant="contained">
              Generate Report
            </Button>
          </DialogActions>
        </Dialog>

        {/* View Report Dialog */}
        <Dialog
          open={viewDialogOpen}
          onClose={() => setViewDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Report Details</DialogTitle>
          <DialogContent>
            {selectedReport && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  {getReportTypeLabel(selectedReport.report_type)}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Period: {new Date(selectedReport.start_date).toLocaleDateString()} - {new Date(selectedReport.end_date).toLocaleDateString()}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Generated: {new Date(selectedReport.generated_at).toLocaleString()}
                </Typography>
                <Box mt={2}>
                  <Typography variant="subtitle1" gutterBottom>
                    Report Data:
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                    <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                      {JSON.stringify(selectedReport.report_data, null, 2)}
                    </pre>
                  </Paper>
                </Box>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
            <Button
              onClick={() => selectedReport && handleDownloadReport(selectedReport.id)}
              variant="contained"
              startIcon={<Download />}
            >
              Download
            </Button>
          </DialogActions>
        </Dialog>

        {/* Actions Menu */}
        <Menu
          anchorEl={menuAnchor}
          open={Boolean(menuAnchor)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => {
            handleViewReport(menuReport?.id);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <Visibility />
            </ListItemIcon>
            <ListItemText>View</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => {
            handleDownloadReport(menuReport?.id);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <Download />
            </ListItemIcon>
            <ListItemText>Download</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => {
            handleDeleteReport(menuReport?.id);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <Assessment />
            </ListItemIcon>
            <ListItemText>Delete</ListItemText>
          </MenuItem>
        </Menu>
      </Box>
    </LocalizationProvider>
  );
};

export default PerformanceReportsPage;
