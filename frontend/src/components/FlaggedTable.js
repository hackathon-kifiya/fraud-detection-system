import React, { useState } from 'react';
import {
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
  Button,
  Typography,
  Box,
  TablePagination,
  Tooltip,
  Alert,
  Grid,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Visibility,
  Security,
} from '@mui/icons-material';

const FlaggedTable = ({ items, onVerify, pagination, totalItems, onPageChange }) => {
  const [selectedItem, setSelectedItem] = useState(null);
  const [verifyDialog, setVerifyDialog] = useState(false);
  const [verifying, setVerifying] = useState(false);

  const handleVerifyClick = (item) => {
    setSelectedItem(item);
    setVerifyDialog(true);
  };

  const handleVerifyConfirm = async (status) => {
    if (!selectedItem) return;
    
    setVerifying(true);
    try {
      await onVerify(selectedItem.id, status);
      setVerifyDialog(false);
      setSelectedItem(null);
    } catch (error) {
      // Error handling is done in parent component
    } finally {
      setVerifying(false);
    }
  };

  const handleCloseDialog = () => {
    setVerifyDialog(false);
    setSelectedItem(null);
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'error';
    if (score >= 70) return 'warning';
    return 'info';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'fraud': return 'error';
      case 'safe': return 'success';
      default: return 'default';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'transaction': return 'primary';
      case 'loan': return 'secondary';
      case 'repayment': return 'info';
      case 'user': return 'warning';
      default: return 'default';
    }
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

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString();
  };

  return (
    <>
      <TableContainer component={Paper} variant="outlined">
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Type</TableCell>
              <TableCell>User ID</TableCell>
              <TableCell>Score</TableCell>
              <TableCell>Reasons</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.id} hover>
                <TableCell>
                  <Chip
                    label={item.type}
                    color={getTypeColor(item.type)}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                
                <TableCell>
                  <Typography variant="body2" fontFamily="monospace">
                    {item.user_id}
                  </Typography>
                </TableCell>
                
                <TableCell>
                  <Chip
                    label={`${item.score.toFixed(1)}`}
                    color={getScoreColor(item.score)}
                    size="small"
                    icon={<Security />}
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
                  <Chip
                    label={item.status}
                    color={getStatusColor(item.status)}
                    size="small"
                  />
                </TableCell>
                
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(item.created_at)}
                  </Typography>
                </TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        onClick={() => handleVerifyClick(item)}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    
                    {item.status === 'pending' && (
                      <>
                        <Tooltip title="Mark as Safe">
                          <IconButton
                            size="small"
                            color="success"
                            onClick={() => onVerify(item.id, 'safe')}
                          >
                            <CheckCircle />
                          </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Mark as Fraud">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => onVerify(item.id, 'fraud')}
                          >
                            <Cancel />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        component="div"
        count={totalItems}
        page={pagination.page - 1}
        onPageChange={(event, newPage) => onPageChange(newPage + 1)}
        rowsPerPage={pagination.limit}
        onRowsPerPageChange={(event) => onPageChange(1)} // Reset to page 1 when changing limit
        rowsPerPageOptions={[25, 50, 100]}
        labelRowsPerPage="Items per page:"
      />

      {/* Verification Dialog */}
      <Dialog open={verifyDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          Flagged Item Details
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Type
                  </Typography>
                  <Chip
                    label={selectedItem.type}
                    color={getTypeColor(selectedItem.type)}
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    User ID
                  </Typography>
                  <Typography variant="body1" fontFamily="monospace">
                    {selectedItem.user_id}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Risk Score
                  </Typography>
                  <Chip
                    label={`${selectedItem.score.toFixed(1)}`}
                    color={getScoreColor(selectedItem.score)}
                    icon={<Security />}
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={selectedItem.status}
                    color={getStatusColor(selectedItem.status)}
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Reasons
                  </Typography>
                  <Typography variant="body1">
                    {formatReasons(selectedItem.reasons)}
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Created At
                  </Typography>
                  <Typography variant="body1">
                    {formatDate(selectedItem.created_at)}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Close
          </Button>
          {selectedItem?.status === 'pending' && (
            <>
              <Button
                color="success"
                startIcon={<CheckCircle />}
                onClick={() => handleVerifyConfirm('safe')}
                disabled={verifying}
              >
                Mark as Safe
              </Button>
              <Button
                color="error"
                startIcon={<Cancel />}
                onClick={() => handleVerifyConfirm('fraud')}
                disabled={verifying}
              >
                Mark as Fraud
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
};

export default FlaggedTable;
