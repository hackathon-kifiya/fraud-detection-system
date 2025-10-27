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
  Chip,
  Divider,
} from "@mui/material";
import {
  PlayArrow as EvaluateIcon,
  Code as CodeIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from "@mui/icons-material";
import { anomalyDetectionAPI } from "../services/api";

const SAMPLE_TRANSACTION = {
  customer_id: "CUST_12345",
  date: "2024-10-25T14:30:00",
  credit: 1000.0,
  debit: 0.0,
  closingBalance: 5000.0,
  narrative: "Cash Deposit BY SELF",
  source: "CASH DEPOSIT",
  is_anomaly: 0,
};

const SAMPLE_KYC = {
  customer_id: "CUST_12345",
  customer_name: "John Doe",
  customer_phone_number: 9123456789,
  customer_age: 35,
  customer_gender: "male",
  customer_marital_status: "single",
  customer_education_level: "primary",
  customer_tin_number: "1234567890",
  customer_bank_account_number: "1234567890",
  customer_region: "ADDIS_ABABA",
  customer_city: "ADDIS_ABABA",
  customer_zone_or_sub_city: "ZONE_1",
  customer_woreda: 1,
  customerId: "CUST_12345",
};

const SAMPLE_MERGED = {
  customer_id: "CUST_12345",
  customer_name: "John Doe",
  customer_phone_number: 9123456789,
  customer_age: 35,
  customer_gender: "male",
  customer_marital_status: "single",
  customer_education_level: "primary",
  customer_tin_number: "1234567890",
  customer_bank_account_number: "1234567890",
  customer_region: "ADDIS_ABABA",
  customer_city: "ADDIS_ABABA",
  customer_zone_or_sub_city: "ZONE_1",
  customer_woreda: 1,
  customerId: "CUST_12345",
  business_id: "BUS_12345",
  business_name: "John's Business",
  business_tin_number: "9876543210",
  business_city: "ADDIS_ABABA",
  business_zone_or_sub_city: "ZONE_1",
  business_woreda: "01",
  business_establishment_year: 2020,
  business_sector: "AGRICULTURE",
  business_level: "GROWING",
  business_starting_capital: 100000.0,
  business_current_capital: 150000.0,
  business_annual_profit: 25000.0,
  business_annual_sales: 200000.0,
  business_current_no_of_employees: 5,
  business_starting_no_of_employees: 2,
  business_source_of_initial_capital: "FAMILY",
  business_association_type: "SOLE_PROPRIETORSHIP",
};

const AnomalyDetectionPage = ({ onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [loadingSample, setLoadingSample] = useState(false);
  const [testData, setTestData] = useState("");
  const [dataType, setDataType] = useState("transaction"); // kyc, transaction, merged
  const [error, setError] = useState(null);
  const [detectionResult, setDetectionResult] = useState(null);

  const getSampleData = () => {
    switch (dataType) {
      case "kyc":
        return SAMPLE_KYC;
      case "merged":
        return SAMPLE_MERGED;
      case "transaction":
      default:
        return SAMPLE_TRANSACTION;
    }
  };

  const handleLoadSample = () => {
    setLoadingSample(true);
    setError(null);
    try {
      const sample = getSampleData();
      setTestData(JSON.stringify(sample, null, 2));
      onShowSnackbar("Sample data loaded successfully", "success");
    } catch (error) {
      setError(error.message);
      onShowSnackbar("Failed to load sample data: " + error.message, "error");
    } finally {
      setLoadingSample(false);
    }
  };

  const handleEvaluate = async () => {
    if (!testData.trim()) {
      onShowSnackbar("Test data is required", "error");
      return;
    }

    let data;
    try {
      data = JSON.parse(testData);
    } catch (e) {
      onShowSnackbar("Invalid JSON format", "error");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let response;
      
      // Call the appropriate API based on data type (using unsupervised models only)
      if (dataType === "kyc") {
        response = await anomalyDetectionAPI.checkKYC(data);
      } else if (dataType === "transaction") {
        response = await anomalyDetectionAPI.checkTransaction(data);
      } else if (dataType === "merged") {
        response = await anomalyDetectionAPI.checkMerged(data);
      }

      setDetectionResult(response.data);
      onShowSnackbar("Anomaly detection completed successfully", "success");
    } catch (error) {
      console.error("Anomaly detection error:", error);
      setError(error.response?.data?.detail || error.message || "Failed to detect anomalies");
      setDetectionResult(null);
      onShowSnackbar("Anomaly detection failed: " + (error.response?.data?.detail || error.message), "error");
    } finally {
      setLoading(false);
    }
  };

  // Load sample data when data type changes
  useEffect(() => {
    const sample = getSampleData();
    setTestData(JSON.stringify(sample, null, 2));
  }, [dataType]);

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case "HIGH":
        return "#d32f2f";
      case "MEDIUM":
        return "#f57c00";
      case "LOW":
        return "#388e3c";
      default:
        return "#424242";
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography
          variant="h4"
          sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
        >
          Anomaly Detection
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Detect anomalies in KYC, transaction, or merged data using Isolation Forest models.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Input Panel */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: "100%" }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
              Input Data
            </Typography>

            {/* Data Type Selection */}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Data Type</InputLabel>
              <Select
                value={dataType}
                onChange={(e) => setDataType(e.target.value)}
                label="Data Type"
              >
                <MenuItem value="transaction">Transaction</MenuItem>
                <MenuItem value="kyc">KYC</MenuItem>
                <MenuItem value="merged">Merged (KYC + Business)</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mb: 2 }}>
              <Button
                variant="outlined"
                startIcon={loadingSample ? <CircularProgress size={20} /> : <CodeIcon />}
                onClick={handleLoadSample}
                disabled={loadingSample}
                fullWidth
              >
                {loadingSample ? "Loading Sample..." : "Load Sample Data"}
              </Button>
            </Box>

            {error && (
              <Alert severity="warning" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            <TextField
              fullWidth
              label="Test Data (JSON)"
              multiline
              rows={18}
              value={testData}
              onChange={(e) => setTestData(e.target.value)}
              placeholder="Enter JSON test data..."
              sx={{
                "& .MuiInputBase-input": {
                  fontFamily: "monospace",
                  fontSize: "0.875rem",
                },
              }}
            />

            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                startIcon={<EvaluateIcon />}
                onClick={handleEvaluate}
                disabled={loading || !testData.trim()}
                fullWidth
                sx={{ bgcolor: "#ff9800", "&:hover": { bgcolor: "#f57c00" } }}
              >
                {loading ? <CircularProgress size={20} /> : "Detect Anomalies"}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Detection Results Panel */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: "100%" }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
              Detection Results
            </Typography>

            {!detectionResult && !loading && (
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
                <Typography variant="h6" sx={{ mb: 1 }}>
                  No detection yet
                </Typography>
                <Typography variant="body2">
                  Enter test data and click "Detect Anomalies" to see results
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
                <Typography variant="body2" sx={{ mt: 2, color: "text.secondary" }}>
                  Detecting anomalies...
                </Typography>
              </Box>
            )}

            {detectionResult && !loading && (
              <Box>
                {/* Anomaly Status Card */}
                <Card
                  sx={{
                    mb: 2,
                    borderRadius: 2,
                    boxShadow: 2,
                    borderLeft: `4px solid ${getRiskColor(detectionResult.risk_level)}`,
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                      {detectionResult.is_anomaly ? (
                        <WarningIcon sx={{ mr: 1, color: getRiskColor(detectionResult.risk_level) }} />
                      ) : (
                        <CheckCircleIcon sx={{ mr: 1, color: "#388e3c" }} />
                      )}
                      <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        {detectionResult.is_anomaly ? "Anomaly Detected" : "Normal"}
                      </Typography>
                      <Chip
                        label={detectionResult.risk_level}
                        sx={{
                          bgcolor: getRiskColor(detectionResult.risk_level),
                          color: "white",
                          fontWeight: "bold",
                        }}
                      />
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Anomaly Score
                        </Typography>
                        <Typography variant="h5" sx={{ fontWeight: "bold" }}>
                          {detectionResult.anomaly_score?.toFixed(4) || "N/A"}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Timestamp
                        </Typography>
                        <Typography variant="body1">
                          {new Date(detectionResult.timestamp).toLocaleString()}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>

                {/* SHAP Explanation */}
                {detectionResult.explanation && (
                  <Card sx={{ mb: 2, borderRadius: 2, boxShadow: 1 }}>
                    <CardContent>
                      <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: "bold" }}>
                        Explanation (SHAP)
                      </Typography>
                      
                      {/* Top Contributing Features */}
                      {detectionResult.explanation.top_contributing_features && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            Top Contributing Features
                          </Typography>
                          {Object.entries(detectionResult.explanation.top_contributing_features)
                            .slice(0, 5)
                            .map(([feature, value]) => (
                              <Box
                                key={feature}
                                sx={{
                                  mb: 1,
                                  p: 1,
                                  bgcolor: "#f5f5f5",
                                  borderRadius: 1,
                                  display: "flex",
                                  justifyContent: "space-between",
                                }}
                              >
                                <Typography variant="body2">{feature}</Typography>
                                <Typography
                                  variant="body2"
                                  sx={{
                                    fontWeight: "bold",
                                    color: Math.abs(value) > 0.1 ? "#d32f2f" : "#388e3c",
                                  }}
                                >
                                  {value.toFixed(4)}
                                </Typography>
                              </Box>
                            ))}
                        </Box>
                      )}

                      {/* Feature Values */}
                      {detectionResult.explanation.feature_values && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            Feature Values
                          </Typography>
                          <Box sx={{ maxHeight: 150, overflowY: "auto" }}>
                            {Object.entries(detectionResult.explanation.feature_values)
                              .slice(0, 10)
                              .map(([feature, value]) => (
                                <Box
                                  key={feature}
                                  sx={{
                                    mb: 0.5,
                                    display: "flex",
                                    justifyContent: "space-between",
                                    fontSize: "0.75rem",
                                  }}
                                >
                                  <Typography variant="caption" color="text.secondary">
                                    {feature}:
                                  </Typography>
                                  <Typography variant="caption">{String(value)}</Typography>
                                </Box>
                              ))}
                          </Box>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                )}

                {/* Raw Response */}
                <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
                  <CardContent>
                    <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: "bold" }}>
                      Raw Response
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={8}
                      value={JSON.stringify(detectionResult, null, 2)}
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

export default AnomalyDetectionPage;

