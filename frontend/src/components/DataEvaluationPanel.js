import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Card,
  CardContent,
} from "@mui/material";
import {
  PlayArrow as EvaluateIcon,
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

const DataEvaluationPanel = ({ onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [loadingSample, setLoadingSample] = useState(false);
  const [testData, setTestData] = useState("");
  const [dataType, setDataType] = useState("");
  const [error, setError] = useState(null);
  const [dataTypes, setDataTypes] = useState([]);
  const [evaluationResult, setEvaluationResult] = useState(null);

  useEffect(() => {
    const loadDataTypes = async () => {
      try {
        const response = await ruleEngineAPI.getAllDataTypes();
        const types = response.data || [];
        setDataTypes(types);
        console.log("Loaded data types:", types);
        
        if (types.length > 0) {
          // Set to the first active data type
          const activeType = types.find(dt => dt.status === 'ACTIVE') || types[0];
          setDataType(activeType.data_type);
          console.log("Setting initial dataType to:", activeType.data_type);
        }
      } catch (error) {
        console.error("Failed to load data types:", error);
      }
    };
    loadDataTypes();
  }, []);

  const handleLoadSample = async () => {
    setLoadingSample(true);
    setError(null);
    
    try {
      console.log("Current dataType state:", dataType);
      console.log("Available dataTypes:", dataTypes);
      
      // dataType is already set to the dataType field (like "transactions", "kyc")
      if (!dataType) {
        console.error("Data type not selected");
        throw new Error("Please select a data type");
      }

      // Get the data type definition from the loaded dataTypes
      const dataTypeDefinition = dataTypes.find(dt => dt.data_type === dataType);
      
      if (!dataTypeDefinition) {
        throw new Error("Data type not found");
      }
      
      console.log("Found data type definition:", dataTypeDefinition);
      
      // Use the sample_data from the data type definition
      let sampleData = dataTypeDefinition.sample_data;
      
      // Handle transactions data which has a nested structure
      if (dataType === 'transactions' && sampleData && sampleData.transactions) {
        sampleData = sampleData.transactions[0]; // Use first transaction
      }
      
      if (!sampleData) {
        throw new Error("No sample data available");
      }

      // Set the test data field with the fetched data
      setTestData(JSON.stringify(sampleData, null, 2));

      onShowSnackbar("Sample data loaded successfully", "success");
    } catch (error) {
      console.error("Failed to load sample data:", error);
      setError(error.response?.data?.message || error.message || "Failed to load sample data");
      onShowSnackbar("Failed to load sample data: " + (error.response?.data?.message || error.message), "error");
      
      // Fallback to local sample data
      setTestData(
        JSON.stringify(SAMPLE_DATA[dataType] || SAMPLE_DATA.transactions, null, 2)
      );
    } finally {
      setLoadingSample(false);
    }
  };

  const handleEvaluate = async () => {
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

    try {
      let response;
      // Use the generic evaluation endpoint with the dataType identifier
      response = await ruleEngineAPI.evaluateGeneric(dataType, facts);

      // Store the evaluation result
      setEvaluationResult(response.data);
      onShowSnackbar("Evaluation completed successfully", "success");
    } catch (error) {
      setError(error.message);
      setEvaluationResult(null);
      onShowSnackbar("Evaluation failed: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography
          variant='h4'
          sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
        >
          Data Evaluation
        </Typography>
        <Typography variant='body1' color='text.secondary'>
          Test data against active fraud detection rules.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Input Panel */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: "100%" }}>
            <Typography variant='h6' sx={{ mb: 2, fontWeight: "bold" }}>
              Input Data
            </Typography>

            <FormControl fullWidth sx={{ mb: 2 }}>
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

            <Box sx={{ mb: 2 }}>
              <Button
                variant='outlined'
                startIcon={loadingSample ? <CircularProgress size={20} /> : <CodeIcon />}
                onClick={handleLoadSample}
                disabled={loadingSample || dataTypes.length === 0}
                fullWidth
              >
                {loadingSample ? "Loading Sample Data..." : "Load Sample Data"}
              </Button>
            </Box>

            {error && (
              <Alert severity="warning" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            <TextField
              fullWidth
              label='Test Data (JSON)'
              multiline
              rows={15}
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

            <Box sx={{ mt: 2 }}>
              <Button
                variant='contained'
                startIcon={<EvaluateIcon />}
                onClick={handleEvaluate}
                disabled={loading || !testData.trim()}
                fullWidth
                sx={{ bgcolor: "#ff9800", "&:hover": { bgcolor: "#f57c00" } }}
              >
                {loading ? <CircularProgress size={20} /> : "Evaluate Data"}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Evaluation Results Panel */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: "100%" }}>
            <Typography variant='h6' sx={{ mb: 2, fontWeight: "bold" }}>
              Evaluation Results
            </Typography>

            {!evaluationResult && !loading && (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  minHeight: 400,
                  textAlign: "center",
                  color: "text.secondary",
                }}
              >
                <Typography variant='h6' sx={{ mb: 1 }}>
                  No evaluation yet
                </Typography>
                <Typography variant='body2'>
                  Enter test data and click "Evaluate Data" to see results
                </Typography>
              </Box>
            )}

            {loading && (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  minHeight: 400,
                }}
              >
                <CircularProgress />
                <Typography variant='body2' sx={{ mt: 2, color: "text.secondary" }}>
                  Evaluating data against rules...
                </Typography>
              </Box>
            )}

            {evaluationResult && !loading && (
              <Box>
                {/* Risk Score and Violations - Side by Side */}
                <Grid container spacing={2} sx={{ mb: 2 }}>
                  {/* Risk Score Card */}
                  <Grid item xs={12} sm={6}>
                    <Card sx={{ borderRadius: 2, boxShadow: 1, height: "100%" }}>
                      <CardContent>
                        <Typography variant='subtitle1' sx={{ mb: 2, fontWeight: "bold" }}>
                          Risk Score
                        </Typography>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <Typography
                            variant='h2'
                            sx={{
                              fontWeight: "bold",
                              color:
                                evaluationResult.normalizedRiskScore === 0
                                  ? "#388e3c"
                                  : evaluationResult.normalizedRiskScore <= 3
                                  ? "#f57c00"
                                  : evaluationResult.normalizedRiskScore <= 6
                                  ? "#ff9800"
                                  : "#d32f2f",
                            }}
                          >
                            {evaluationResult.normalizedRiskScore || 0}
                          </Typography>
                          <Typography variant='h6' sx={{ ml: 1, color: "text.secondary" }}>
                            / 10
                          </Typography>
                        </Box>
                        <Typography variant='body2' color='text.secondary' sx={{ mt: 1, textAlign: "center" }}>
                          {evaluationResult.normalizedRiskScore === 0
                            ? "No risk detected"
                            : evaluationResult.normalizedRiskScore <= 3
                            ? "Low risk"
                            : evaluationResult.normalizedRiskScore <= 6
                            ? "Medium risk"
                            : evaluationResult.normalizedRiskScore <= 10
                            ? "High risk"
                            : "Critical risk"}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Violations Count Card */}
                  <Grid item xs={12} sm={6}>
                    <Card sx={{ borderRadius: 2, boxShadow: 1, height: "100%" }}>
                      <CardContent>
                        <Typography variant='subtitle1' sx={{ mb: 2, fontWeight: "bold" }}>
                          Violations
                        </Typography>
                        <Typography
                          variant='h2'
                          sx={{
                            fontWeight: "bold",
                            color: evaluationResult.violationsCount > 0 ? "#d32f2f" : "#388e3c",
                            textAlign: "center",
                          }}
                        >
                          {evaluationResult.violationsCount || 0}
                        </Typography>
                        <Typography variant='body2' color='text.secondary' sx={{ textAlign: "center" }}>
                          Rule violations detected
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Violations List */}
                {evaluationResult.violations && evaluationResult.violations.length > 0 && (
                  <Card sx={{ mb: 2, borderRadius: 2, boxShadow: 1 }}>
                    <CardContent>
                      <Typography variant='subtitle1' sx={{ mb: 2, fontWeight: "bold" }}>
                        Violation Details
                      </Typography>
                      {evaluationResult.violations.map((violation, index) => (
                        <Box
                          key={index}
                          sx={{
                            mb: 1,
                            p: 2,
                            bgcolor: "#ffebee",
                            borderRadius: 1,
                            borderLeft: "3px solid #d32f2f",
                          }}
                        >
                          <Typography variant='body1' sx={{ fontWeight: "bold" }}>
                            {violation.code}
                          </Typography>
                          <Typography variant='body2' color='text.secondary'>
                            Weight: {violation.weight} | {violation.description}
                          </Typography>
                        </Box>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Raw Response (Optional) */}
                <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
                  <CardContent>
                    <Typography variant='subtitle1' sx={{ mb: 2, fontWeight: "bold" }}>
                      Raw Response
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={6}
                      value={JSON.stringify(evaluationResult, null, 2)}
                      InputProps={{
                        readOnly: true,
                        sx: {
                          "& .MuiInputBase-input": {
                            fontFamily: "monospace",
                            fontSize: "0.875rem",
                          },
                        },
                      }}
                    />
                  </CardContent>
                </Card>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DataEvaluationPanel;
