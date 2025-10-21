import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Button,
  Alert,
  CircularProgress,
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
} from '@mui/material';
import { 
  Security, 
  CheckCircle, 
  Cancel, 
  Search,
  Visibility,
  Add as AddIcon,
} from '@mui/icons-material';
import { flaggedAPI } from '../services/api';

const Dashboard = ({ onShowSnackbar }) => {
  const [flaggedItems, setFlaggedItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [filters, setFilters] = useState({
    status: '',
    type: '',
    user_id: '',
  });
  const [pagination, setPagination] = useState({
    page: 0,
    rowsPerPage: 10,
  });
  const [totalItems, setTotalItems] = useState(0);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {
        ...filters,
        page: pagination.page + 1,
        limit: pagination.rowsPerPage,
        sort_by: 'created_at',
        sort_order: 'desc',
      };

      const response = await flaggedAPI.getAll(params);
      setFlaggedItems(response.data.items || []);
      setTotalItems(response.data.total || 0);
    } catch (error) {
      onShowSnackbar(`Failed to load flagged items: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters, pagination]);

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

  const handleVerify = async (itemId, status) => {
    try {
      await flaggedAPI.verify(itemId, { status });
      onShowSnackbar(`Item marked as ${status}`, 'success');
      await loadData(); // Refresh the data
    } catch (error) {
      onShowSnackbar(`Failed to verify item: ${error.message}`, 'error');
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

  if (loading && flaggedItems.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper sx={{ borderRadius: 2, boxShadow: 1, overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: '1px solid #e0e0e0' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#424242' }}>
            Flagged Items Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            sx={{ 
              bgcolor: '#ff9800', 
              '&:hover': { bgcolor: '#f57c00' },
              borderRadius: 2,
              px: 3,
              py: 1
            }}
          >
            Run Detection
          </Button>
        </Box>

        {/* Search and Filter Bar */}
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            placeholder="Search by User ID, Type or Reasons..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            size="small"
            sx={{ 
              minWidth: 300,
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
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
              sx={{ borderRadius: 2 }}
            >
              <MenuItem value="All">All</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="fraud">Fraud</MenuItem>
              <MenuItem value="safe">Safe</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Table */}
      <Box>
        <Typography variant="h6" sx={{ p: 2, pb: 1, fontWeight: 'bold', color: '#424242' }}>
          Flagged Items ({totalItems} total)
        </Typography>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
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
                  <TableCell colSpan={7} sx={{ textAlign: 'center', py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : flaggedItems.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} sx={{ textAlign: 'center', py: 4 }}>
                    <Alert severity="info">No flagged items found with the current filters.</Alert>
                  </TableCell>
                </TableRow>
              ) : (
                flaggedItems.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>
                      <Chip
                        label={item.type}
                        size="small"
                        sx={{ 
                          bgcolor: '#e3f2fd', 
                          color: '#1976d2',
                          fontWeight: 'bold'
                        }}
                      />
                    </TableCell>
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

        {/* Pagination */}
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

export default Dashboard;

