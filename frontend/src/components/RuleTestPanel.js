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

const RuleTestPanel = ({ open, rule, onClose, onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [testData, setTestData] = useState("");
  const [dataType, setDataType] = useState("TRANSACTION");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [dataTypes, setDataTypes] = useState([]);

  useEffect(() => {
    const loadDataTypes = async () => {
      try {
        const response = await ruleEngineAPI.getAllDataTypes();
        setDataTypes(response.data || []);
        if (response.data && response.data.length > 0) {
          setDataType(response.data[0].dataType);
        }
      } catch (error) {
        console.error("Failed to load data types:", error);
      }
    };
    loadDataTypes();
  }, []);

  useEffect(() => {
    if (open && rule) {
      setDataType(rule.dataType);
      setTestData(
        JSON.stringify(
          SAMPLE_DATA[rule.dataType] || SAMPLE_DATA.TRANSACTION,
          null,
          2
        )
      );
      setResults(null);
      setError(null);
    }
  }, [open, rule]);

  const handleLoadSample = () => {
    setTestData(
      JSON.stringify(SAMPLE_DATA[dataType] || SAMPLE_DATA.TRANSACTION, null, 2)
    );
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
                      <MenuItem key={dt.id} value={dt.name}>
                        {dt.displayName || dt.name}
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
