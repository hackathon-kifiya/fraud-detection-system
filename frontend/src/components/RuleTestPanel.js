import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Alert,
  CircularProgress,
  IconButton,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Chip,
  Grid,
} from "@mui/material";
import {
  Close as CloseIcon,
  PlayArrow as TestIcon,
  Code as CodeIcon,
} from "@mui/icons-material";
import { ruleEngineAPI } from "../services/api";

const SAMPLE_DATA = {
  transactions: {
    customer_id: "CUST_12345",
    date: "2024-10-25T14:30:00",
    credit: 1000,
    debit: 0,
    closingBalance: 5000,
    narrative: "Cash Deposit BY SELF",
    source: "CASH DEPOSIT",
    is_anomaly: 0,
  },
  kyc: {
    customer_id: "CUST_12345",
    customer_name: "John Doe",
    customer_age: 35,
    customer_gender: "male",
    customer_marital_status: "single",
    customer_education_level: "primary",
    customer_phone_number: 9123456789,
    customer_tin_number: "1234567890",
    customer_bank_account_number: "1234567890000",
    customer_region: "ADDIS_ABABA",
    customer_city: "ADDIS_ABABA",
    customer_zone_or_sub_city: "ZONE_1",
    customer_woreda: 1,
    business_id: "BUS_12345",
    business_name: "John's Business",
    business_sector: "AGRICULTURE",
    business_level: "GROWING",
    business_tin_number: "9876543210",
    business_current_capital: 150000,
    business_current_no_of_employees: 5,
  },
};

const RuleTestPanel = ({ open, rule, onClose, onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [testData, setTestData] = useState("");
  const [dataType, setDataType] = useState("");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [dataTypes, setDataTypes] = useState([]);

  useEffect(() => {
    const loadDataTypes = async () => {
      try {
        const response = await ruleEngineAPI.getAllDataTypes();
        setDataTypes(response.data || []);
        if (response.data && response.data.length > 0) {
          setDataType(response.data[0].data_type);
        }
      } catch (error) {
        console.error("Failed to load data types:", error);
      }
    };
    loadDataTypes();
  }, []);

  useEffect(() => {
    if (open && rule) {
      // Get sample data from data type definition
      const dataTypeDefinition = dataTypes.find(dt => dt.data_type === rule.dataType);
      
      if (dataTypeDefinition && dataTypeDefinition.sample_data) {
        let sampleData = dataTypeDefinition.sample_data;
        
        // Handle transactions data which has a nested structure
        if (rule.dataType === 'transactions' && sampleData.transactions) {
          sampleData = sampleData.transactions[0];
        }
        
        setDataType(rule.dataType);
        setTestData(JSON.stringify(sampleData, null, 2));
      } else {
        // Fallback to local sample data
        setDataType(rule.dataType);
        setTestData(
          JSON.stringify(
            SAMPLE_DATA[rule.dataType] || SAMPLE_DATA.transactions,
            null,
            2
          )
        );
      }
      setResults(null);
      setError(null);
    }
  }, [open, rule, dataTypes]);

  const handleLoadSample = () => {
    // Get sample data from data type definition
    const dataTypeDefinition = dataTypes.find(dt => dt.data_type === dataType);
    
    if (dataTypeDefinition && dataTypeDefinition.sample_data) {
      let sampleData = dataTypeDefinition.sample_data;
      
      // Handle transactions data which has a nested structure
      if (dataType === 'transactions' && sampleData.transactions) {
        sampleData = sampleData.transactions[0];
      }
      
      setTestData(JSON.stringify(sampleData, null, 2));
    } else {
      // Fallback to local sample data
      setTestData(
        JSON.stringify(SAMPLE_DATA[dataType] || SAMPLE_DATA.transactions, null, 2)
      );
    }
  };

  const handleTestRule = async () => {
    if (!testData.trim()) {
      onShowSnackbar("Test data is required", "error");
      return;
    }

    let facts;
    try {
      facts = JSON.parse(testData);
      if (!Array.isArray(facts)) {
        facts = [facts];
      }
    } catch (e) {
      onShowSnackbar("Invalid JSON format", "error");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Use the generic evaluation endpoint
      const response = await ruleEngineAPI.evaluateGeneric(dataType.toLowerCase(), facts);
      setResults(response.data);
      onShowSnackbar("Rule test completed successfully", "success");
    } catch (error) {
      setError(error.message);
      onShowSnackbar("Rule test failed: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const getRiskScoreColor = (score) => {
    if (score >= 80) return "error";
    if (score >= 60) return "warning";
    if (score >= 40) return "info";
    return "success";
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth='lg'
      fullWidth
      PaperProps={{
        sx: {
          height: "90vh",
          maxHeight: "90vh",
        },
      }}
    >
      <DialogTitle>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Typography variant='h6' sx={{ fontWeight: "bold" }}>
            Test Rule: {rule?.name || "Unknown Rule"}
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ p: 3 }}>
          <Grid container spacing={3}>
            {/* Test Data Input */}
            <Grid item xs={12} md={6}>
              <Typography variant='h6' sx={{ mb: 2, fontWeight: "bold" }}>
                Test Data
              </Typography>

              <Box sx={{ mb: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Data Type</InputLabel>
                  <Select
                    value={dataType}
                    onChange={(e) => setDataType(e.target.value)}
                    label='Data Type'
                  >
                    {dataTypes.filter(dt => dt.status === 'ACTIVE').map((dt) => (
                      <MenuItem key={dt.data_type} value={dt.data_type}>
                        {dt.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Button
                  variant='outlined'
                  startIcon={<CodeIcon />}
                  onClick={handleLoadSample}
                  fullWidth
                >
                  Load Sample Data
                </Button>
              </Box>

              <TextField
                fullWidth
                label='Test Data (JSON)'
                multiline
                rows={12}
                value={testData}
                onChange={(e) => setTestData(e.target.value)}
                placeholder='Enter JSON test data...'
                sx={{
                  "& .MuiInputBase-input": {
                    fontFamily: "monospace",
                    fontSize: "0.875rem",
                  },
                }}
              />
            </Grid>

            {/* Test Results */}
            <Grid item xs={12} md={6}>
              <Typography variant='h6' sx={{ mb: 2, fontWeight: "bold" }}>
                Test Results
              </Typography>

              {loading && (
                <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
                  <CircularProgress />
                </Box>
              )}

              {error && (
                <Alert severity='error' sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {results && (
                <Box>
                  {/* Summary Card */}
                  <Card sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography
                        variant='h6'
                        sx={{ mb: 2, fontWeight: "bold" }}
                      >
                        Evaluation Summary
                      </Typography>

                      <Grid container spacing={2}>
                        <Grid item xs={4}>
                          <Typography variant='body2' color='text.secondary'>
                            Risk Score
                          </Typography>
                          <Chip
                            label={`${results.riskScore || 0}`}
                            color={getRiskScoreColor(results.riskScore || 0)}
                            size='small'
                            sx={{ fontWeight: "bold" }}
                          />
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant='body2' color='text.secondary'>
                            Violations
                          </Typography>
                          <Chip
                            label={`${results.violationsCount || 0}`}
                            color={results.violationsCount > 0 ? "error" : "success"}
                            size='small'
                            sx={{ fontWeight: "bold" }}
                          />
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant='body2' color='text.secondary'>
                            Entity ID
                          </Typography>
                          <Typography variant='body2' sx={{ fontWeight: "bold", wordBreak: "break-all" }}>
                            {results.entityId || "N/A"}
                          </Typography>
                        </Grid>
                      </Grid>

                      {results.violations && results.violations.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography
                            variant='body2'
                            color='text.secondary'
                            sx={{ mb: 1 }}
                          >
                            Violations ({results.violations.length})
                          </Typography>
                          {results.violations.map((violation, index) => (
                            <Chip
                              key={index}
                              label={`${violation.code} (${violation.weight} pts)`}
                              size='small'
                              color='error'
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ))}
                        </Box>
                      )}
                    </CardContent>
                  </Card>

                  {/* Detailed Results */}
                  <Card>
                    <CardContent>
                      <Typography
                        variant='h6'
                        sx={{ mb: 2, fontWeight: "bold" }}
                      >
                        Detailed Results
                      </Typography>
                      <TextField
                        fullWidth
                        multiline
                        value={JSON.stringify(results, null, 2)}
                        InputProps={{
                          readOnly: true,
                          sx: {
                            fontFamily: "monospace",
                            fontSize: "0.875rem",
                            "& .MuiInputBase-input": {
                              fontFamily: "monospace",
                              fontSize: "0.875rem",
                            },
                          },
                        }}
                        sx={{
                          "& .MuiInputBase-root": {
                            backgroundColor: "#f9f9f9",
                            maxHeight: "400px",
                            overflow: "auto",
                          },
                        }}
                      />
                    </CardContent>
                  </Card>
                </Box>
              )}
            </Grid>
          </Grid>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, borderTop: 1, borderColor: "divider" }}>
        <Button onClick={onClose}>Close</Button>
        <Button
          onClick={handleTestRule}
          variant='contained'
          startIcon={<TestIcon />}
          disabled={loading || !testData.trim()}
          sx={{ bgcolor: "#ff9800", "&:hover": { bgcolor: "#f57c00" } }}
        >
          {loading ? <CircularProgress size={20} /> : "Test Rule"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RuleTestPanel;
