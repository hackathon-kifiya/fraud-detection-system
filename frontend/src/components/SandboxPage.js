import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Chip,
  TextField,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider,
  LinearProgress,
} from '@mui/material';
import { 
  Security, 
  Search, 
  Visibility, 
  CheckCircle, 
  Cancel,
  Refresh as RefreshIcon,
  PlayArrow,
  AccountBalance,
  CreditCard,
  Assessment,
  Person,
  Payment,
} from '@mui/icons-material';
import FileUpload from './FileUpload';
import { uploadAPI, detectionAPI, flaggedAPI } from '../services/api';

const SandboxPage = ({ onShowSnackbar }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [detectionRunning, setDetectionRunning] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [flaggedItems, setFlaggedItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [pagination, setPagination] = useState({
    page: 0,
    rowsPerPage: 10,
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [detectionResult, setDetectionResult] = useState(null);
  const [showDetectionDialog, setShowDetectionDialog] = useState(false);

  const dataTypes = [
    { key: 'transactions', label: 'Transactions', icon: AccountBalance },
    { key: 'loan_requests', label: 'Loan Requests', icon: CreditCard },
    { key: 'credit_history', label: 'Credit History', icon: Assessment },
    { key: 'kyc', label: 'KYC Data', icon: Person },
    { key: 'repayments', label: 'Repayments', icon: Payment },
  ];

  const currentDataType = dataTypes[activeTab];

  const loadFlaggedItems = async () => {
    try {
      setLoading(true);
      const params = {
        type: currentDataType.key,
        page: pagination.page + 1,
        limit: pagination.rowsPerPage,
        search: searchTerm,
        sort_by: 'created_at',
        sort_order: 'desc',
      };
      const response = await flaggedAPI.getAll(params);
      setFlaggedItems(response.data.items || []);
      setTotalItems(response.data.total || 0);
    } catch (error) {
      onShowSnackbar(`Failed to load flagged ${currentDataType.key}: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      let response;
      switch (currentDataType.key) {
        case 'transactions':
          response = await uploadAPI.transactions(formData);
          break;
        case 'loan_requests':
          response = await uploadAPI.loanRequests(formData);
          break;
        case 'credit_history':
          response = await uploadAPI.creditHistory(formData);
          break;
        case 'kyc':
          response = await uploadAPI.kyc(formData);
          break;
        case 'repayments':
          response = await uploadAPI.repayments(formData);
          break;
        default:
          throw new Error('Unknown data type');
      }
      
      setUploadResult({
        success: true,
        count: response.data.count,
        message: response.data.message,
      });
      onShowSnackbar(`${currentDataType.label} uploaded successfully (${response.data.count} records)`, 'success');
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Upload failed';
      setUploadResult({
        success: false,
        error: errorMessage,
      });
      onShowSnackbar(`Failed to upload ${currentDataType.key}: ${errorMessage}`, 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleDetection = async () => {
    setDetectionRunning(true);
    try {
      const response = await detectionAPI.triggerByType(currentDataType.key, { days_back: 30 });
      
      // Store detection result
      setDetectionResult({
        dataType: currentDataType.label,
        response: response.data,
        flaggedCount: response.data?.flagged_count || 0,
        totalProcessed: response.data?.total_processed || 0,
        flaggedItems: response.data?.flagged_items || []
      });
      
      // Show popup with results
      setShowDetectionDialog(true);
      
      onShowSnackbar(`${currentDataType.label} fraud detection completed`, 'success');
      await loadFlaggedItems(); // Refresh flagged items after detection
    } catch (error) {
      onShowSnackbar(`${currentDataType.label} detection failed: ${error.message}`, 'error');
    } finally {
      setDetectionRunning(false);
    }
  };

  const handleVerify = async (itemId, status) => {
    try {
      await flaggedAPI.verify(itemId, { status });
      onShowSnackbar(`Item marked as ${status}`, 'success');
      await loadFlaggedItems(); // Refresh the data
    } catch (error) {
      onShowSnackbar(`Failed to verify item: ${error.message}`, 'error');
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setUploadResult(null);
    setSearchTerm('');
    setPagination({ page: 0, rowsPerPage: 10 });
  };

  useEffect(() => {
    loadFlaggedItems();
  }, [pagination, searchTerm, activeTab]);

  const handleChangePage = (event, newPage) => {
    setPagination(prev => ({
      ...prev,
      page: newPage,
    }));
  };

  const handleChangeRowsPerPage = (event) => {
    setPagination(prev => ({
      ...prev,
      rowsPerPage: parseInt(event.target.value, 10),
      page: 0,
    }));
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString();
  };

  const formatReasons = (reasonsStr) => {
    try {
      const reasons = JSON.parse(reasonsStr);
      if (Array.isArray(reasons)) {
        return reasons.join(', ');
      }
      return reasonsStr;
    } catch {
      return reasonsStr;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return '#ff9800';
      case 'fraud': return '#f44336';
      case 'safe': return '#4caf50';
      default: return '#9e9e9e';
    }
  };

  const getStatusBackgroundColor = (status) => {
    switch (status) {
      case 'pending': return '#fff3e0';
      case 'fraud': return '#ffebee';
      case 'safe': return '#e8f5e8';
      default: return '#f5f5f5';
    }
  };

  return (
    <Paper sx={{ borderRadius: 2, boxShadow: 1, overflow: 'hidden' }}>
      <Box sx={{ p: 3, borderBottom: '1px solid #e0e0e0' }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#424242', mb: 1 }}>
          Fraud Detection Sandbox
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload data and run fraud detection analysis in a sandbox environment.
        </Typography>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="data type tabs">
          {dataTypes.map((dataType, index) => {
            const IconComponent = dataType.icon;
            return (
              <Tab
                key={dataType.key}
                icon={<IconComponent />}
                label={dataType.label}
                iconPosition="start"
                sx={{
                  minHeight: 60,
                  textTransform: 'none',
                  fontWeight: 'bold',
                }}
              />
            );
          })}
        </Tabs>
      </Box>

      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 2, boxShadow: 1, height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#424242' }}>
                  Upload {currentDataType.label} Data
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Upload your {currentDataType.key} CSV file for fraud analysis in the sandbox environment.
                </Typography>
                
                <FileUpload
                  onUpload={handleUpload}
                  disabled={uploading}
                  accept=".csv"
                />
                
                {uploadResult && (
                  <Box sx={{ mt: 2 }}>
                    {uploadResult.success ? (
                      <Alert severity="success" sx={{ borderRadius: 2 }}>
                        {uploadResult.message}
                      </Alert>
                    ) : (
                      <Alert severity="error" sx={{ borderRadius: 2 }}>
                        {uploadResult.error}
                      </Alert>
                    )}
                  </Box>
                )}

                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={handleDetection}
                  disabled={detectionRunning || !uploadResult?.success}
                  sx={{ 
                    mt: 3, 
                    bgcolor: '#ff9800', 
                    '&:hover': { bgcolor: '#f57c00' },
                    borderRadius: 2,
                    px: 3,
                    py: 1
                  }}
                >
                  {detectionRunning ? 'Running Detection...' : `Run ${currentDataType.label} Detection`}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 2, boxShadow: 1, height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#424242' }}>
                  Instructions
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  1. Upload your {currentDataType.key} CSV file using the upload area
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  2. Click "Run {currentDataType.label} Detection" to analyze the data
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  3. Review the flagged items in the table below
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  4. Use the action buttons to verify or mark items as safe/fraud
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

      </Box>

      {/* Detection Results Dialog */}
      <Dialog 
        open={showDetectionDialog} 
        onClose={() => setShowDetectionDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle sx={{ 
          bgcolor: '#f5f5f5', 
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}>
          <Security sx={{ color: '#ff9800' }} />
          <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242' }}>
            Fraud Detection Review - {detectionResult?.dataType}
          </Typography>
        </DialogTitle>
        
        <DialogContent sx={{ p: 3 }}>
          {detectionResult && (
            <Box>
              {/* Review Process Stats */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={3}>
                  <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1, bgcolor: '#e3f2fd' }}>
                    <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                      {detectionResult.totalProcessed}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Analyzed
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={3}>
                  <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1, bgcolor: '#fff3e0' }}>
                    <Typography variant="h4" color="warning" sx={{ fontWeight: 'bold' }}>
                      {flaggedItems.filter(item => item.status === 'pending').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Awaiting Review
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={3}>
                  <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1, bgcolor: '#ffebee' }}>
                    <Typography variant="h4" color="error" sx={{ fontWeight: 'bold' }}>
                      {flaggedItems.filter(item => item.status === 'fraud').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Confirmed Fraud
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={3}>
                  <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1, bgcolor: '#e8f5e8' }}>
                    <Typography variant="h4" color="success" sx={{ fontWeight: 'bold' }}>
                      {flaggedItems.filter(item => item.status === 'safe').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      False Positives
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Review Progress */}
              <Paper sx={{ p: 2, mb: 3, bgcolor: '#f9f9f9', borderRadius: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242', mb: 2 }}>
                  Review Progress
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ flexGrow: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={flaggedItems.length > 0 ? ((flaggedItems.filter(item => item.status !== 'pending').length / flaggedItems.length) * 100) : 0}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {flaggedItems.filter(item => item.status !== 'pending').length} of {flaggedItems.length} reviewed
                  </Typography>
                </Box>
              </Paper>

              <Divider sx={{ my: 2 }} />

              {/* Detection Response Details */}
              <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242', mb: 2 }}>
                Detection Analysis Summary
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, bgcolor: '#e8f5e8', borderRadius: 2, border: '1px solid #4caf50' }}>
                    <Typography variant="h6" sx={{ color: '#2e7d32', fontWeight: 'bold', mb: 1 }}>
                      ✅ Analysis Completed
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Detection engine successfully processed {detectionResult.totalProcessed} records
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, bgcolor: '#fff3e0', borderRadius: 2, border: '1px solid #ff9800' }}>
                    <Typography variant="h6" sx={{ color: '#f57c00', fontWeight: 'bold', mb: 1 }}>
                      ⚠️ Suspicious Activity Detected
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {detectionResult.flaggedCount} cases require human review
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Detection Metrics */}
              <Paper sx={{ p: 3, bgcolor: '#f9f9f9', borderRadius: 2, mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242', mb: 2 }}>
                  Detection Metrics
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                        {detectionResult.totalProcessed}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Records Analyzed
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="error" sx={{ fontWeight: 'bold' }}>
                        {detectionResult.flaggedCount}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Flagged Cases
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="success" sx={{ fontWeight: 'bold' }}>
                        {detectionResult.totalProcessed - detectionResult.flaggedCount}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Clean Records
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="warning" sx={{ fontWeight: 'bold' }}>
                        {detectionResult.totalProcessed > 0 ? ((detectionResult.flaggedCount / detectionResult.totalProcessed) * 100).toFixed(1) : 0}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Flag Rate
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Paper>

              {/* Flagged Items Review Table */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242' }}>
                  Cases Requiring Human Review ({flaggedItems.length} total)
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={loadFlaggedItems}
                  size="small"
                  sx={{ borderRadius: 2 }}
                >
                  Refresh
                </Button>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <TextField
                  placeholder={`Search ${currentDataType.key}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  size="small"
                  fullWidth
                  sx={{ 
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>
              
              <TableContainer component={Paper} sx={{ borderRadius: 2, boxShadow: 1, maxHeight: 400 }}>
                <Table stickyHeader>
                  <TableHead>
                    <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                      <TableCell sx={{ fontWeight: 'bold' }}>Case ID</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Risk Score</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Fraud Indicators</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Detection Date</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Review Status</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Review Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {loading ? (
                      <TableRow>
                        <TableCell colSpan={6} sx={{ textAlign: 'center', py: 4 }}>
                          <CircularProgress />
                        </TableCell>
                      </TableRow>
                    ) : flaggedItems.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} sx={{ textAlign: 'center', py: 4 }}>
                          <Alert severity="info">No cases requiring review found.</Alert>
                        </TableCell>
                      </TableRow>
                    ) : (
                      flaggedItems.map((item) => (
                        <TableRow 
                          key={item.id} 
                          hover
                          sx={{ 
                            '&:hover': { bgcolor: item.status === 'pending' ? '#fff3e0' : '#f5f5f5' },
                            bgcolor: item.status === 'pending' ? '#fef7e0' : 'inherit'
                          }}
                        >
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace" sx={{ fontWeight: 'bold' }}>
                              {item.user_id}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Case #{item.id}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Chip
                                label={`${item.score.toFixed(1)}`}
                                size="small"
                                sx={{ 
                                  bgcolor: item.score >= 85 ? '#ffebee' : item.score >= 70 ? '#fff3e0' : '#e8f5e8',
                                  color: item.score >= 85 ? '#d32f2f' : item.score >= 70 ? '#f57c00' : '#388e3c',
                                  fontWeight: 'bold'
                                }}
                                icon={<Security sx={{ fontSize: 16 }} />}
                              />
                              {item.score >= 85 && (
                                <Chip
                                  label="HIGH RISK"
                                  size="small"
                                  sx={{ 
                                    bgcolor: '#ffebee',
                                    color: '#d32f2f',
                                    fontWeight: 'bold',
                                    fontSize: '0.7rem'
                                  }}
                                />
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Tooltip title={formatReasons(item.reasons)} arrow>
                              <Typography
                                variant="body2"
                                sx={{
                                  maxWidth: 200,
                                  overflow: 'hidden',
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap',
                                }}
                              >
                                {formatReasons(item.reasons)}
                              </Typography>
                            </Tooltip>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(item.created_at)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={item.status === 'pending' ? 'Needs Review' : item.status === 'fraud' ? 'Confirmed Fraud' : 'False Positive'}
                              size="small"
                              sx={{
                                bgcolor: getStatusBackgroundColor(item.status),
                                color: getStatusColor(item.status),
                                fontWeight: 'bold',
                                textTransform: 'capitalize'
                              }}
                            />
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Tooltip title="View Case Details">
                                <IconButton size="small" color="primary">
                                  <Visibility />
                                </IconButton>
                              </Tooltip>
                              
                              {item.status === 'pending' && (
                                <>
                                  <Tooltip title="Approve as Safe (False Positive)">
                                    <IconButton
                                      size="small"
                                      color="success"
                                      onClick={() => handleVerify(item.id, 'safe')}
                                      sx={{ 
                                        '&:hover': { 
                                          bgcolor: '#e8f5e8',
                                          transform: 'scale(1.1)'
                                        }
                                      }}
                                    >
                                      <CheckCircle />
                                    </IconButton>
                                  </Tooltip>
                                  
                                  <Tooltip title="Confirm as Fraud">
                                    <IconButton
                                      size="small"
                                      color="error"
                                      onClick={() => handleVerify(item.id, 'fraud')}
                                      sx={{ 
                                        '&:hover': { 
                                          bgcolor: '#ffebee',
                                          transform: 'scale(1.1)'
                                        }
                                      }}
                                    >
                                      <Cancel />
                                    </IconButton>
                                  </Tooltip>
                                </>
                              )}
                              
                              {item.status !== 'pending' && (
                                <Tooltip title="Reopen for Review">
                                  <IconButton
                                    size="small"
                                    color="warning"
                                    onClick={() => handleVerify(item.id, 'pending')}
                                  >
                                    <RefreshIcon />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2, borderTop: '1px solid #e0e0e0' }}>
                <Typography variant="body2" color="text.secondary">
                  0 of {totalItems} row(s) selected.
                </Typography>
                <TablePagination
                  component="div"
                  count={totalItems}
                  page={pagination.page}
                  onPageChange={handleChangePage}
                  rowsPerPage={pagination.rowsPerPage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                  rowsPerPageOptions={[10, 25, 50, 100]}
                  labelRowsPerPage="Rows per page:"
                  labelDisplayedRows={({ from, to, count }) => `Page ${pagination.page + 1} of ${Math.ceil(count / pagination.rowsPerPage)}`}
                />
              </Box>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ p: 3, borderTop: '1px solid #e0e0e0', bgcolor: '#f9f9f9' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
            <Typography variant="body2" color="text.secondary">
              💡 <strong>Review Process:</strong> Each flagged case requires human review to determine if it's genuine fraud or a false positive.
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button 
              onClick={() => setShowDetectionDialog(false)}
              variant="outlined"
              sx={{ borderRadius: 2 }}
            >
              Close Review
            </Button>
            <Button 
              onClick={() => {
                setShowDetectionDialog(false);
                onShowSnackbar('Review session closed. Cases remain in pending status until reviewed.', 'info');
              }}
              variant="contained"
              sx={{ 
                bgcolor: '#ff9800', 
                '&:hover': { bgcolor: '#f57c00' },
                borderRadius: 2
              }}
            >
              Complete Review Session
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default SandboxPage;