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
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';
import { userAPI, adminAPI } from '../services/api';

const AuditorManagementPage = ({ onShowSnackbar }) => {
  const [auditors, setAuditors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    role: 'analyst',
    is_active: true,
  });
  const [auditorStats, setAuditorStats] = useState({});

  useEffect(() => {
    fetchAuditors();
  }, []);

  useEffect(() => {
    if (auditors.length > 0) {
      fetchAuditorStats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auditors.length]);

  const fetchAuditors = async () => {
    setLoading(true);
    try {
      const response = await userAPI.getUsers({});
      const auditorsOnly = response.data.users.filter(user => user.role === 'analyst');
      setAuditors(auditorsOnly);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch auditors');
    } finally {
      setLoading(false);
    }
  };

  const fetchAuditorStats = async () => {
    try {
      // Fetch workload stats for all auditors
      const response = await adminAPI.getAuditorWorkload();
      const workloads = response.data.workload || [];
      
      // Create a map of auditor ID to stats
      const stats = {};
      workloads.forEach(workload => {
        // Calculate total cases (active + completed this week)
        const totalCases = (workload.active_assignments || 0) + (workload.completed_this_week || 0);
        stats[workload.auditor_id] = {
          totalCases: totalCases,
          activeCases: workload.active_assignments || 0,
          completedToday: workload.completed_today || 0,
        };
      });
      
      // For auditors not in workload list, set default values
      auditors.forEach(auditor => {
        if (!stats[auditor.id]) {
          stats[auditor.id] = {
            totalCases: 0,
            activeCases: 0,
            completedToday: 0,
          };
        }
      });
      
      setAuditorStats(stats);
    } catch (err) {
      console.error('Failed to fetch auditor stats:', err);
      // Set default values for all auditors
      const stats = {};
      auditors.forEach(auditor => {
        stats[auditor.id] = {
          totalCases: 0,
          activeCases: 0,
          completedToday: 0,
        };
      });
      setAuditorStats(stats);
    }
  };

  const handleOpenDialog = (user = null) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
        role: user.role,
        is_active: user.is_active,
      });
    } else {
      setEditingUser(null);
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        role: 'analyst',
        is_active: true,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingUser(null);
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      role: 'analyst',
      is_active: true,
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
      if (editingUser) {
        await userAPI.updateUser(editingUser.id, formData);
        onShowSnackbar('Auditor updated successfully', 'success');
      } else {
        await userAPI.register(formData);
        onShowSnackbar('Auditor created successfully', 'success');
      }
      handleCloseDialog();
      fetchAuditors();
    } catch (err) {
      setError(err.response?.data?.error || 'Operation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this auditor?')) {
      try {
        await userAPI.deleteUser(userId);
        onShowSnackbar('Auditor deleted successfully', 'success');
        fetchAuditors();
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete auditor');
      }
    }
  };

  const getStatsForAuditor = (auditorId) => {
    return auditorStats[auditorId] || { totalCases: 0, activeCases: 0, completedToday: 0 };
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Auditor Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ bgcolor: '#ff9800', '&:hover': { bgcolor: '#f57c00' } }}
        >
          Add Auditor
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Summary Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ borderRadius: 2, boxShadow: 1, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 2,
                    bgcolor: '#e3f2fd',
                    color: '#1976d2',
                    mr: 2,
                  }}
                >
                  <AssignmentIcon sx={{ fontSize: 24 }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 'bold', fontSize: '1rem' }}>
                  Total Auditors
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#1976d2', fontSize: '2.5rem' }}>
                {auditors.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ borderRadius: 2, boxShadow: 1, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 2,
                    bgcolor: '#f3e5f5',
                    color: '#7b1fa2',
                    mr: 2,
                  }}
                >
                  <AssignmentIcon sx={{ fontSize: 24 }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 'bold', fontSize: '1rem' }}>
                  Active Auditors
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#7b1fa2', fontSize: '2.5rem' }}>
                {auditors.filter(a => a.is_active).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ borderRadius: 2, boxShadow: 1, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 2,
                    bgcolor: '#fff3e0',
                    color: '#f57c00',
                    mr: 2,
                  }}
                >
                  <AssignmentIcon sx={{ fontSize: 24 }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 'bold', fontSize: '1rem' }}>
                  Total Cases
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold', color: '#f57c00', fontSize: '2.5rem' }}>
                {Object.values(auditorStats).reduce((sum, stat) => sum + (stat.totalCases || 0), 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper>
        <TableContainer>
          <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Total Cases</TableCell>
              <TableCell>Active Cases</TableCell>
              <TableCell>Completed Today</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : auditors.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No auditors found
                </TableCell>
              </TableRow>
            ) : (
              auditors.map((auditor) => {
                const stats = getStatsForAuditor(auditor.id);
                return (
                  <TableRow key={auditor.id}>
                    <TableCell>
                      {auditor.first_name} {auditor.last_name}
                    </TableCell>
                    <TableCell>{auditor.email}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          {stats.totalCases}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={stats.activeCases}
                        size="small"
                        color="warning"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={stats.completedToday}
                        size="small"
                        color="success"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={auditor.is_active ? 'Active' : 'Inactive'}
                        color={auditor.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(auditor)}
                        color="primary"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(auditor.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
        </TableContainer>
      </Paper>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {editingUser ? 'Edit Auditor' : 'Add New Auditor'}
          </DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              label="First Name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Last Name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              margin="normal"
              required
              disabled={!!editingUser}
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
            <Button type="submit" variant="contained" disabled={loading}>
              {loading ? <CircularProgress size={24} /> : editingUser ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default AuditorManagementPage;

