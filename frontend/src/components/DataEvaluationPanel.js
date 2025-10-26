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
  TRANSACTION: {
    entityId: "txn-123",
    amount: 15000.0,
    accountBalance: 5000.0,
    type: "debit",
    paymentMethod: "card",
    timestamp: "2025-10-25T10:30:00Z",
  },
  KYC: {
    entityId: "user-456",
    verifiedStatus: false,
    documentType: "passport",
    documentNumber: "A1234567",
    issueDate: "2020-01-15",
    expiryDate: "2030-01-15",
  },
  LOAN: {
    entityId: "loan-789",
    amount: 75000.0,
    interestRate: 8.5,
    termMonths: 36,
    applicantIncome: 50000.0,
    creditScore: 650,
  },
  CREDIT: {
    entityId: "credit-101",
    score: 580,
    historyLength: 24,
    utilizationRate: 0.85,
    latePayments: 3,
    inquiries: 5,
  },
  REPAYMENT: {
    entityId: "repay-202",
    isLate: true,
    daysPastDue: 15,
    amount: 2500.0,
    originalDueDate: "2025-10-10",
    currentBalance: 10000.0,
  },
};

const DataEvaluationPanel = ({ onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [loadingSample, setLoadingSample] = useState(false);
  const [testData, setTestData] = useState("");
  const [dataType, setDataType] = useState("TRANSACTION");
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
          setDataType(activeType.dataType);
          console.log("Setting initial dataType to:", activeType.dataType);
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

      console.log("Calling API with dataType:", dataType);
      
      // Fetch sample data from CSV
      const response = await ruleEngineAPI.getSampleData(dataType, 5);
      const sampleRecords = response.data || [];
      
      if (sampleRecords.length === 0) {
        throw new Error("No sample data available");
      }

      // Convert CSV records to JSON array format
      const factsArray = sampleRecords.map(record => {
        const fact = {};
        // Convert all string values, keeping them as strings but try to parse numbers
        Object.keys(record).forEach(key => {
          const value = record[key];
          // Try to parse as number, if it fails, keep as string
          if (!isNaN(value) && value !== '') {
            const num = parseFloat(value);
            if (!isNaN(num)) {
              fact[key] = Number.isInteger(num) ? parseInt(value) : parseFloat(value);
            } else {
              fact[key] = value;
            }
          } else {
            fact[key] = value;
          }
        });
        return fact;
      });

      // Set the test data field with the fetched data
      if (factsArray.length === 1) {
        setTestData(JSON.stringify(factsArray[0], null, 2));
      } else {
        setTestData(JSON.stringify(factsArray, null, 2));
      }

      onShowSnackbar("Sample data loaded successfully", "success");
    } catch (error) {
      console.error("Failed to load sample data:", error);
      setError(error.response?.data?.message || error.message || "Failed to load sample data");
      onShowSnackbar("Failed to load sample data: " + (error.response?.data?.message || error.message), "error");
      
      // Fallback to local sample data (map lowercase dataType to uppercase key)
      const dataTypeKey = dataType.toUpperCase();
      setTestData(
        JSON.stringify(SAMPLE_DATA[dataTypeKey] || SAMPLE_DATA.TRANSACTION, null, 2)
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
                  <MenuItem key={dt.id} value={dt.dataType}>
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
