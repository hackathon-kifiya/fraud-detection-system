import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Button,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';
import FileUpload from './FileUpload';
import { uploadAPI, detectionAPI } from '../services/api';

const UploadPage = ({ onShowSnackbar }) => {
  const [uploading, setUploading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [detectingType, setDetectingType] = useState(null);
  const [uploadResults, setUploadResults] = useState({});
  const [detectionResult, setDetectionResult] = useState(null);
  const [individualResults, setIndividualResults] = useState({});

  const uploadConfigs = [
    {
      key: 'transactions',
      title: 'Transactions',
      description: 'Upload transaction history data',
      endpoint: uploadAPI.transactions,
      required: false,
    },
    {
      key: 'loan_requests',
      title: 'Loan Requests',
      description: 'Upload loan application data',
      endpoint: uploadAPI.loanRequests,
      required: false,
    },
    {
      key: 'credit_history',
      title: 'Credit History',
      description: 'Upload credit scores and history',
      endpoint: uploadAPI.creditHistory,
      required: false,
    },
    {
      key: 'kyc',
      title: 'KYC Data',
      description: 'Upload Know Your Customer information',
      endpoint: uploadAPI.kyc,
      required: false,
    },
    {
      key: 'repayments',
      title: 'Repayments',
      description: 'Upload loan repayment data',
      endpoint: uploadAPI.repayments,
      required: false,
    },
  ];

  const handleUpload = async (key, file) => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const config = uploadConfigs.find(c => c.key === key);
      const response = await config.endpoint(formData);
      
      setUploadResults(prev => ({
        ...prev,
        [key]: {
          success: true,
          count: response.data.count,
          message: response.data.message,
        }
      }));
      
      onShowSnackbar(`${config.title} uploaded successfully (${response.data.count} records)`, 'success');
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Upload failed';
      setUploadResults(prev => ({
        ...prev,
        [key]: {
          success: false,
          error: errorMessage,
        }
      }));
      
      onShowSnackbar(`Failed to upload ${uploadConfigs.find(c => c.key === key).title}: ${errorMessage}`, 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleDetection = async () => {
    // Check if all required uploads are successful
    const requiredKeys = uploadConfigs.filter(c => c.required).map(c => c.key);
    const allUploaded = requiredKeys.every(key => uploadResults[key]?.success);
    
    if (!allUploaded) {
      onShowSnackbar('Please upload all required data files before running detection', 'warning');
      return;
    }

    setDetecting(true);
    setDetectionResult(null);

    try {
      const response = await detectionAPI.trigger({ days_back: 30 });
      setDetectionResult(response.data);
      onShowSnackbar(`Detection completed: ${response.data.result.total_flagged} items flagged`, 'success');
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Detection failed';
      onShowSnackbar(`Detection failed: ${errorMessage}`, 'error');
    } finally {
      setDetecting(false);
    }
  };

  const handleIndividualDetection = async (dataType) => {
    // Check if this data type has been uploaded
    if (!uploadResults[dataType]?.success) {
      onShowSnackbar(`Please upload ${dataType} data first`, 'warning');
      return;
    }

    setDetectingType(dataType);
    setIndividualResults(prev => ({ ...prev, [dataType]: null }));

    try {
      const response = await detectionAPI.triggerByType(dataType, { days_back: 30 });
      setIndividualResults(prev => ({ ...prev, [dataType]: response.data }));
      onShowSnackbar(`${dataType} detection completed: ${response.data.result.total_flagged} items flagged`, 'success');
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Detection failed';
      onShowSnackbar(`${dataType} detection failed: ${errorMessage}`, 'error');
    } finally {
      setDetectingType(null);
    }
  };

  const getUploadStatus = (key) => {
    const result = uploadResults[key];
    if (!result) return 'pending';
    return result.success ? 'success' : 'error';
  };

  const canRunDetection = () => {
    const requiredKeys = uploadConfigs.filter(c => c.required).map(c => c.key);
    return requiredKeys.every(key => uploadResults[key]?.success);
  };

  return (
    <Paper sx={{ borderRadius: 2, boxShadow: 1, overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: '1px solid #e0e0e0' }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#424242', mb: 1 }}>
          Data Upload
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload your data files to perform fraud detection analysis. You can run detection on individual data types or all data together.
        </Typography>
      </Box>

      {/* Upload Cards */}
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {uploadConfigs.map((config) => (
            <Grid item xs={12} md={6} key={config.key}>
              <Card sx={{ borderRadius: 2, boxShadow: 1, '&:hover': { boxShadow: 3 } }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#424242' }}>
                    {config.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {config.description}
                  </Typography>
                  
                  <FileUpload
                    onUpload={(file) => handleUpload(config.key, file)}
                    disabled={uploading}
                    accept=".csv"
                  />
                  
                  {uploadResults[config.key] && (
                    <Box sx={{ mt: 2 }}>
                      {uploadResults[config.key].success ? (
                        <Alert severity="success" sx={{ borderRadius: 2 }}>
                          {uploadResults[config.key].message}
                        </Alert>
                      ) : (
                        <Alert severity="error" sx={{ borderRadius: 2 }}>
                          {uploadResults[config.key].error}
                        </Alert>
                      )}
                    </Box>
                  )}

                  {uploadResults[config.key]?.success && (
                    <Box sx={{ mt: 2 }}>
                      <Button
                        variant="outlined"
                        color="primary"
                        startIcon={<PlayArrow />}
                        onClick={() => handleIndividualDetection(config.key)}
                        disabled={detectingType === config.key}
                        fullWidth
                        sx={{ borderRadius: 2 }}
                      >
                        {detectingType === config.key ? 'Detecting...' : `Detect ${config.title} Fraud`}
                      </Button>
                      
                      {individualResults[config.key] && (
                        <Box sx={{ mt: 1 }}>
                          <Alert severity="info" sx={{ borderRadius: 2 }}>
                            Detection completed: {individualResults[config.key].result.total_flagged} items flagged
                          </Alert>
                        </Box>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Detection Section */}
      <Box sx={{ p: 3, borderTop: '1px solid #e0e0e0', bgcolor: '#fafafa' }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: '#424242' }}>
          Fraud Detection
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Run fraud detection analysis on the uploaded data. This will analyze all data and flag suspicious items.
        </Typography>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#424242' }}>
            Upload Status
          </Typography>
          <Grid container spacing={2}>
            {uploadConfigs.map((config) => (
              <Grid item xs={12} sm={6} md={4} key={config.key}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      backgroundColor: 
                        getUploadStatus(config.key) === 'success' ? '#4caf50' :
                        getUploadStatus(config.key) === 'error' ? '#f44336' : '#9e9e9e'
                    }}
                  />
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {config.title}: {getUploadStatus(config.key)}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 3 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<PlayArrow />}
            onClick={handleDetection}
            disabled={!canRunDetection() || detecting}
            sx={{ 
              minWidth: 200,
              bgcolor: '#ff9800',
              '&:hover': { bgcolor: '#f57c00' },
              borderRadius: 2,
              px: 4,
              py: 1.5
            }}
          >
            {detecting ? 'Running Detection...' : 'Run Fraud Detection'}
          </Button>
        </Box>

        {detecting && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress sx={{ borderRadius: 1 }} />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Analyzing data and detecting fraud patterns...
            </Typography>
          </Box>
        )}

        {detectionResult && (
          <Box sx={{ mt: 3 }}>
            <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>
              Detection completed successfully!
            </Alert>
            
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#424242' }}>
              Detection Results
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {detectionResult.result?.total_flagged || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Flagged
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                  <Typography variant="h4" color="error" sx={{ fontWeight: 'bold' }}>
                    {detectionResult.result?.high_risk_count || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    High Risk
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                  <Typography variant="h4" color="warning.main" sx={{ fontWeight: 'bold' }}>
                    {Object.keys(detectionResult.result?.flagged_by_user || {}).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Users Affected
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1 }}>
                  <Typography variant="h4" color="info.main" sx={{ fontWeight: 'bold' }}>
                    {Object.keys(detectionResult.result?.flagged_by_type || {}).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Types Flagged
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default UploadPage;
