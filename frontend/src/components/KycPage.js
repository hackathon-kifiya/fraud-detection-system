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
} from '@mui/material';
import { 
  Security, 
  Search, 
  Visibility, 
  CheckCircle, 
  Cancel,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { flaggedAPI } from '../services/api';

const KycPage = ({ onShowSnackbar }) => {
  const [loading, setLoading] = useState(true);
  const [flaggedItems, setFlaggedItems] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [pagination, setPagination] = useState({
    page: 0,
    rowsPerPage: 10,
  });
  const [searchTerm, setSearchTerm] = useState('');

  const loadFlaggedItems = async () => {
    try {
      setLoading(true);
      const params = {
        type: 'kyc',
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
      onShowSnackbar(`Failed to load flagged KYC data: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (itemId, status) => {
    try {
      await flaggedAPI.verify(itemId, { status });
      onShowSnackbar(`Item marked as ${status}`, 'success');
      await loadFlaggedItems();
    } catch (error) {
      onShowSnackbar(`Failed to verify item: ${error.message}`, 'error');
    }
  };

  useEffect(() => {
    loadFlaggedItems();
  }, [pagination, searchTerm]);

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
          KYC Data Fraud Detection
        </Typography>
        <Typography variant="body1" color="text.secondary">
          View and manage flagged KYC data fraud detection results.
        </Typography>
      </Box>

      <Grid container spacing={3} sx={{ p: 3 }}>
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#424242' }}>
                Detection Statistics
              </Typography>
              <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                    <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                      {totalItems}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Flagged
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                    <Typography variant="h4" color="error" sx={{ fontWeight: 'bold' }}>
                      {flaggedItems.filter(item => item.score >= 85).length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      High Risk
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                    <Typography variant="h4" color="warning" sx={{ fontWeight: 'bold' }}>
                      {flaggedItems.filter(item => item.status === 'pending').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Pending Review
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                    <Typography variant="h4" color="success" sx={{ fontWeight: 'bold' }}>
                      {flaggedItems.filter(item => item.status === 'safe').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Verified Safe
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ p: 3, borderTop: '1px solid #e0e0e0', bgcolor: '#fafafa' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242' }}>
            Flagged KYC Data ({totalItems} total)
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
            placeholder="Search KYC data..."
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
        
        <TableContainer component={Paper} sx={{ borderRadius: 2, boxShadow: 1 }}>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 'bold' }}>User ID</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Risk Score</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Reasons</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Created Date</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
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
                    <Alert severity="info">No flagged KYC data found.</Alert>
                  </TableCell>
                </TableRow>
              ) : (
                flaggedItems.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace" sx={{ fontWeight: 'bold' }}>
                        {item.user_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
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
                        label={item.status}
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
                        <Tooltip title="View Details">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        
                        {item.status === 'pending' && (
                          <>
                            <Tooltip title="Mark as Safe">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => handleVerify(item.id, 'safe')}
                              >
                                <CheckCircle />
                              </IconButton>
                            </Tooltip>
                            
                            <Tooltip title="Mark as Fraud">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleVerify(item.id, 'fraud')}
                              >
                                <Cancel />
                              </IconButton>
                            </Tooltip>
                          </>
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
    </Paper>
  );
};

export default KycPage;