import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Add as AddIcon,
  DataObject as DataObjectIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

const DataSynthesisPage = ({ onShowSnackbar }) => {
  const [generating, setGenerating] = useState(false);
  const [dataType, setDataType] = useState('transactions');
  const [recordCount, setRecordCount] = useState(100);
  const [fraudPercentage, setFraudPercentage] = useState(20);
  const [includeHealthy, setIncludeHealthy] = useState(true);
  const [includeSuspicious, setIncludeSuspicious] = useState(true);
  const [generatedData, setGeneratedData] = useState(null);

  const dataTypes = [
    { key: 'transactions', label: 'Transactions', icon: DataObjectIcon, description: 'Financial transaction data' },
    { key: 'loan_requests', label: 'Loan Requests', icon: SecurityIcon, description: 'Loan application data' },
    { key: 'credit_history', label: 'Credit History', icon: CheckCircleIcon, description: 'Credit score and history' },
    { key: 'kyc', label: 'KYC Data', icon: WarningIcon, description: 'Know Your Customer information' },
    { key: 'repayments', label: 'Repayments', icon: RefreshIcon, description: 'Loan repayment records' },
  ];

  const handleGenerateData = async () => {
    setGenerating(true);
    try {
      // Simulate data generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const healthyCount = includeHealthy ? Math.floor(recordCount * (1 - fraudPercentage / 100)) : 0;
      const suspiciousCount = includeSuspicious ? Math.floor(recordCount * (fraudPercentage / 100)) : 0;
      
      setGeneratedData({
        dataType,
        totalRecords: recordCount,
        healthyRecords: healthyCount,
        suspiciousRecords: suspiciousCount,
        timestamp: new Date().toISOString(),
        filename: `${dataType}_synthetic_${Date.now()}.csv`
      });
      
      onShowSnackbar(`Generated ${recordCount} ${dataType} records successfully`, 'success');
    } catch (error) {
      onShowSnackbar(`Failed to generate data: ${error.message}`, 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadData = () => {
    if (generatedData) {
      // Simulate CSV download
      const csvContent = `user_id,amount,timestamp,type,payment_method,risk_score,is_fraud
user_001,150.00,2024-01-15T10:30:00Z,debit,card,25,false
user_002,2500.00,2024-01-15T11:45:00Z,credit,transfer,85,true
user_003,75.50,2024-01-15T14:20:00Z,debit,card,30,false`;
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = generatedData.filename;
      a.click();
      window.URL.revokeObjectURL(url);
      
      onShowSnackbar('Data downloaded successfully', 'success');
    }
  };

  const handleUploadToSandbox = () => {
    if (generatedData) {
      onShowSnackbar('Data uploaded to sandbox successfully', 'success');
      // In a real implementation, this would upload the generated data to the sandbox
    }
  };

  const currentDataTypeInfo = dataTypes.find(dt => dt.key === dataType);

  return (
    <Paper sx={{ borderRadius: 2, boxShadow: 1, overflow: 'hidden' }}>
      <Box sx={{ p: 3, borderBottom: '1px solid #e0e0e0' }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#424242', mb: 1 }}>
          Data Synthesis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate synthetic data for testing fraud detection algorithms in the sandbox environment.
        </Typography>
      </Box>

      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {/* Configuration Panel */}
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 2, boxShadow: 1, height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#424242' }}>
                  Data Generation Configuration
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Data Type</InputLabel>
                    <Select
                      value={dataType}
                      onChange={(e) => setDataType(e.target.value)}
                      label="Data Type"
                    >
                      {dataTypes.map((type) => {
                        const IconComponent = type.icon;
                        return (
                          <MenuItem key={type.key} value={type.key}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <IconComponent sx={{ fontSize: 20 }} />
                              <Box>
                                <Typography variant="body1">{type.label}</Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {type.description}
                                </Typography>
                              </Box>
                            </Box>
                          </MenuItem>
                        );
                      })}
                    </Select>
                  </FormControl>

                  <Box sx={{ mb: 2 }}>
                    <Typography gutterBottom>Number of Records: {recordCount}</Typography>
                    <Slider
                      value={recordCount}
                      onChange={(e, value) => setRecordCount(value)}
                      min={10}
                      max={1000}
                      step={10}
                      marks={[
                        { value: 10, label: '10' },
                        { value: 500, label: '500' },
                        { value: 1000, label: '1000' }
                      ]}
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography gutterBottom>Fraud Percentage: {fraudPercentage}%</Typography>
                    <Slider
                      value={fraudPercentage}
                      onChange={(e, value) => setFraudPercentage(value)}
                      min={0}
                      max={100}
                      step={5}
                      marks={[
                        { value: 0, label: '0%' },
                        { value: 50, label: '50%' },
                        { value: 100, label: '100%' }
                      ]}
                    />
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={includeHealthy}
                          onChange={(e) => setIncludeHealthy(e.target.checked)}
                        />
                      }
                      label="Include Healthy Records"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={includeSuspicious}
                          onChange={(e) => setIncludeSuspicious(e.target.checked)}
                        />
                      }
                      label="Include Suspicious Records"
                    />
                  </Box>

                  <Button
                    variant="contained"
                    startIcon={generating ? <CircularProgress size={20} /> : <AddIcon />}
                    onClick={handleGenerateData}
                    disabled={generating || (!includeHealthy && !includeSuspicious)}
                    fullWidth
                    sx={{ 
                      bgcolor: '#1976d2', 
                      '&:hover': { bgcolor: '#1565c0' },
                      borderRadius: 2,
                      py: 1.5
                    }}
                  >
                    {generating ? 'Generating Data...' : 'Generate Data'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Results Panel */}
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 2, boxShadow: 1, height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#424242' }}>
                  Generated Data
                </Typography>
                
                {generatedData ? (
                  <Box>
                    <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>
                      Data generation completed successfully!
                    </Alert>
                    
                    <Box sx={{ mb: 3 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1, bgcolor: '#e8f5e8' }}>
                            <Typography variant="h4" color="success" sx={{ fontWeight: 'bold' }}>
                              {generatedData.healthyRecords}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Healthy Records
                            </Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={6}>
                          <Paper sx={{ p: 2, textAlign: 'center', borderRadius: 2, boxShadow: 1, bgcolor: '#ffebee' }}>
                            <Typography variant="h4" color="error" sx={{ fontWeight: 'bold' }}>
                              {generatedData.suspiciousRecords}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Suspicious Records
                            </Typography>
                          </Paper>
                        </Grid>
                      </Grid>
                    </Box>

                    <Box sx={{ mb: 3 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        File: {generatedData.filename}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Generated: {new Date(generatedData.timestamp).toLocaleString()}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Button
                        variant="outlined"
                        startIcon={<DownloadIcon />}
                        onClick={handleDownloadData}
                        sx={{ borderRadius: 2 }}
                      >
                        Download CSV
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={<UploadIcon />}
                        onClick={handleUploadToSandbox}
                        sx={{ 
                          bgcolor: '#ff9800', 
                          '&:hover': { bgcolor: '#f57c00' },
                          borderRadius: 2
                        }}
                      >
                        Upload to Sandbox
                      </Button>
                    </Box>
                  </Box>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <DataObjectIcon sx={{ fontSize: 64, color: '#e0e0e0', mb: 2 }} />
                    <Typography variant="body1" color="text.secondary">
                      Configure and generate synthetic data to get started
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Data Types Overview */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242', mb: 2 }}>
            Supported Data Types
          </Typography>
          
          <Grid container spacing={2}>
            {dataTypes.map((type) => {
              const IconComponent = type.icon;
              return (
                <Grid item xs={12} sm={6} md={4} key={type.key}>
                  <Card sx={{ 
                    borderRadius: 2, 
                    boxShadow: 1,
                    '&:hover': { boxShadow: 3 },
                    cursor: 'pointer',
                    border: dataType === type.key ? '2px solid #1976d2' : '1px solid #e0e0e0'
                  }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ 
                          p: 1, 
                          borderRadius: 2, 
                          bgcolor: dataType === type.key ? '#e3f2fd' : '#f5f5f5', 
                          color: dataType === type.key ? '#1976d2' : '#666',
                          mr: 2
                        }}>
                          <IconComponent sx={{ fontSize: 20 }} />
                        </Box>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#424242' }}>
                          {type.label}
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {type.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </Box>
      </Box>
    </Paper>
  );
};

export default DataSynthesisPage;

