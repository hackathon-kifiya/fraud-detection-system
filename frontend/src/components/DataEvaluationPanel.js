import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  PlayArrow as EvaluateIcon,
  Code as CodeIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
} from "@mui/icons-material";
import ReactJson from "react-json-view";
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
  const [dataType, setDataType] = useState("TRANSACTION");
  const [testData, setTestData] = useState("");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleLoadSample = () => {
    setTestData(
      JSON.stringify(SAMPLE_DATA[dataType] || SAMPLE_DATA.TRANSACTION, null, 2)
    );
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
    setResults(null);

    try {
      let response;
      switch (dataType) {
        case "TRANSACTION":
          response = await ruleEngineAPI.evaluateTransaction(facts);
          break;
        case "KYC":
          response = await ruleEngineAPI.evaluateKYC(facts);
          break;
        case "LOAN":
          response = await ruleEngineAPI.evaluateLoan(facts);
          break;
        case "CREDIT":
          response = await ruleEngineAPI.evaluateCredit(facts);
          break;
        case "REPAYMENT":
          response = await ruleEngineAPI.evaluateRepayment(facts);
          break;
        default:
          response = await ruleEngineAPI.evaluateGeneric(dataType, facts);
      }

      setResults(response.data);
      onShowSnackbar("Evaluation completed successfully", "success");
    } catch (error) {
      setError(error.message);
      onShowSnackbar("Evaluation failed: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleExportResults = () => {
    if (!results) return;

    const dataStr = JSON.stringify(results, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);

    const exportFileDefaultName = `evaluation-results-${dataType.toLowerCase()}-${
      new Date().toISOString().split("T")[0]
    }.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();
  };

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case "PASS":
        return "success";
      case "REVIEW":
        return "warning";
      case "FAIL":
        return "error";
      default:
        return "default";
    }
  };

  const getVerdictIcon = (verdict) => {
    switch (verdict) {
      case "PASS":
        return <SuccessIcon />;
      case "REVIEW":
        return <WarningIcon />;
      case "FAIL":
        return <ErrorIcon />;
      default:
        return <CodeIcon />;
    }
  };

  const getRiskScoreColor = (score) => {
    if (score >= 80) return "error";
    if (score >= 60) return "warning";
    if (score >= 40) return "info";
    return "success";
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
                <MenuItem value='TRANSACTION'>Transaction</MenuItem>
                <MenuItem value='KYC'>KYC</MenuItem>
                <MenuItem value='LOAN'>Loan</MenuItem>
                <MenuItem value='CREDIT'>Credit</MenuItem>
                <MenuItem value='REPAYMENT'>Repayment</MenuItem>
              </Select>
            </FormControl>

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

        {/* Results Panel */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: "100%" }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                mb: 2,
              }}
            >
              <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                Evaluation Results
              </Typography>
              {results && (
                <Tooltip title='Export Results'>
                  <IconButton onClick={handleExportResults}>
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Box>

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

            {results ? (
              <Box>
                {/* Summary Card */}
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant='h6' sx={{ mb: 2, fontWeight: "bold" }}>
                      Evaluation Summary
                    </Typography>

                    <Grid container spacing={2}>
                      <Grid item xs={6}>
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
                      <Grid item xs={6}>
                        <Typography variant='body2' color='text.secondary'>
                          Verdict
                        </Typography>
                        <Chip
                          icon={getVerdictIcon(results.verdict)}
                          label={results.verdict || "UNKNOWN"}
                          color={getVerdictColor(results.verdict)}
                          size='small'
                          sx={{ fontWeight: "bold" }}
                        />
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
                    <Typography variant='h6' sx={{ mb: 2, fontWeight: "bold" }}>
                      Detailed Results
                    </Typography>
                    <ReactJson
                      src={results}
                      theme='monokai'
                      collapsed={1}
                      displayDataTypes={false}
                      displayObjectSize={false}
                      enableClipboard={false}
                      style={{
                        backgroundColor: "#f5f5f5",
                        padding: "12px",
                        borderRadius: "4px",
                        fontSize: "12px",
                        maxHeight: "300px",
                        overflow: "auto",
                      }}
                    />
                  </CardContent>
                </Card>
              </Box>
            ) : (
              <Card>
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      py: 4,
                      color: "text.secondary",
                    }}
                  >
                    <CodeIcon sx={{ fontSize: 48, mb: 2 }} />
                    <Typography variant='body1'>
                      Enter test data and click "Evaluate Data" to see results
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DataEvaluationPanel;
