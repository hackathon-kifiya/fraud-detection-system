import React, { useState, useEffect } from 'react';
import {
  Box,
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Webhook as WebhookIcon,
} from '@mui/icons-material';
import { callbackAPI } from '../services/api';

const IntegrationSettingsPage = ({ onShowSnackbar }) => {
  const [callbacks, setCallbacks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCallback, setEditingCallback] = useState(null);
  const [formData, setFormData] = useState({
    data_type: '',
    callback_url: '',
    method: 'POST',
    is_active: true,
    headers: '',
  });

  const dataTypes = [
    { value: 'transactions', label: 'Transactions' },
    { value: 'loan_requests', label: 'Loan Requests' },
    { value: 'credit_history', label: 'Credit History' },
    { value: 'kyc', label: 'KYC Data' },
    { value: 'repayments', label: 'Repayments' },
    { value: 'flagged_items', label: 'Flagged Items' },
  ];

  const httpMethods = [
    { value: 'POST', label: 'POST' },
    { value: 'PUT', label: 'PUT' },
    { value: 'PATCH', label: 'PATCH' },
  ];

  useEffect(() => {
    fetchCallbacks();
  }, []);

  const fetchCallbacks = async () => {
    setLoading(true);
    try {
      const response = await callbackAPI.getAll({});
      setCallbacks(response.data.callbacks || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch callbacks');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (callback = null) => {
    if (callback) {
      setEditingCallback(callback);
      setFormData({
        data_type: callback.data_type,
        callback_url: callback.callback_url,
        method: callback.method,
        is_active: callback.is_active,
        headers: callback.headers || '',
      });
    } else {
      setEditingCallback(null);
      setFormData({
        data_type: '',
        callback_url: '',
        method: 'POST',
        is_active: true,
        headers: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingCallback(null);
    setFormData({
      data_type: '',
      callback_url: '',
      method: 'POST',
      is_active: true,
      headers: '',
    });
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (editingCallback) {
        await callbackAPI.update(editingCallback.id, formData);
        onShowSnackbar('Callback updated successfully', 'success');
      } else {
        await callbackAPI.create(formData);
        onShowSnackbar('Callback created successfully', 'success');
      }
      handleCloseDialog();
      fetchCallbacks();
    } catch (err) {
      setError(err.response?.data?.error || 'Operation failed');
      onShowSnackbar(err.response?.data?.error || 'Operation failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (callbackId) => {
    if (window.confirm('Are you sure you want to delete this callback?')) {
      try {
        await callbackAPI.delete(callbackId);
        onShowSnackbar('Callback deleted successfully', 'success');
        fetchCallbacks();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete callback');
        onShowSnackbar(err.response?.data?.error || 'Failed to delete callback', 'error');
      }
    }
  };

  const getDataTypeLabel = (type) => {
    const dataType = dataTypes.find(dt => dt.value === type);
    return dataType ? dataType.label : type;
  };

  const getMethodColor = (method) => {
    switch (method) {
      case 'POST': return 'success';
      case 'PUT': return 'warning';
      case 'PATCH': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Integration Settings
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ bgcolor: '#ff9800', '&:hover': { bgcolor: '#f57c00' } }}
        >
          Add Callback
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Data Type</TableCell>
                <TableCell>Callback URL</TableCell>
                <TableCell>Method</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : callbacks.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No callbacks configured
                  </TableCell>
                </TableRow>
              ) : (
                callbacks.map((callback) => (
                  <TableRow key={callback.id}>
                    <TableCell>
                      <Chip
                        label={getDataTypeLabel(callback.data_type)}
                        color="primary"
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {callback.callback_url}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={callback.method}
                        color={getMethodColor(callback.method)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={callback.is_active ? 'Active' : 'Inactive'}
                        color={callback.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(callback.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(callback)}
                        color="primary"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(callback.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {editingCallback ? 'Edit Callback' : 'Add New Callback'}
          </DialogTitle>
          <DialogContent>
            <FormControl fullWidth margin="normal">
              <InputLabel>Data Type</InputLabel>
              <Select
                name="data_type"
                value={formData.data_type}
                onChange={handleChange}
                label="Data Type"
                required
              >
                {dataTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Callback URL"
              name="callback_url"
              value={formData.callback_url}
              onChange={handleChange}
              margin="normal"
              required
              placeholder="https://example.com/api/callbacks"
              helperText="Enter the full URL where webhook will be sent"
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>HTTP Method</InputLabel>
              <Select
                name="method"
                value={formData.method}
                onChange={handleChange}
                label="HTTP Method"
                required
              >
                {httpMethods.map((method) => (
                  <MenuItem key={method.value} value={method.value}>
                    {method.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Custom Headers (JSON)"
              name="headers"
              value={formData.headers}
              onChange={handleChange}
              margin="normal"
              multiline
              rows={3}
              placeholder='{"Authorization": "Bearer token", "X-Custom-Header": "value"}'
              helperText="Optional: JSON object with custom headers to include in requests"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={handleChange}
                  name="is_active"
                />
              }
              label="Active"
              sx={{ mt: 2 }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              sx={{ bgcolor: '#ff9800', '&:hover': { bgcolor: '#f57c00' } }}
            >
              {loading ? <CircularProgress size={24} /> : (editingCallback ? 'Update' : 'Create')}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default IntegrationSettingsPage;

