import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Slider,
  Button,
  Alert,
  CircularProgress,
  Divider,
  Paper,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
} from "@mui/material";
import {
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Person as PersonIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
} from "@mui/icons-material";
import { riskAggregationAPI } from "../services/api";

const RiskDecisionPage = ({ onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [riskParams, setRiskParams] = useState({
    autoRejectThreshold: 85,
    autoApproveThreshold: 25,
    humanReviewMin: 25,
    humanReviewMax: 85,
  });

  const [currentRiskScore, setCurrentRiskScore] = useState(65);
  const [selectedModel, setSelectedModel] = useState("default");
  const [isModelBased, setIsModelBased] = useState(false);
  const [isThresholdModelBased, setIsThresholdModelBased] = useState(false);
  const [engineWeights, setEngineWeights] = useState({
    ruleEngine: 40,
    anomalyDetection: 35,
    predictiveModel: 25,
  });

  const loadRiskParameters = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would fetch from backend
      // const response = await riskAggregationAPI.getParameters();
      // setRiskParams(response.data);
    } catch (error) {
      onShowSnackbar("Failed to load risk parameters", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleParameterChange = (parameter, value) => {
    setRiskParams((prev) => ({
      ...prev,
      [parameter]: value,
    }));
  };

  const handleEngineWeightChange = (engine, value) => {
    setEngineWeights((prev) => {
      const newWeights = { ...prev, [engine]: value };

      // Ensure weights sum to 100 by adjusting other engines proportionally
      const total = Object.values(newWeights).reduce(
        (sum, weight) => sum + weight,
        0
      );
      if (total !== 100) {
        const otherEngines = Object.keys(newWeights).filter(
          (key) => key !== engine
        );
        const remainingWeight = 100 - value;
        const otherTotal = otherEngines.reduce(
          (sum, key) => sum + newWeights[key],
          0
        );

        if (otherTotal > 0) {
          otherEngines.forEach((key) => {
            newWeights[key] = Math.round(
              (newWeights[key] / otherTotal) * remainingWeight
            );
          });
        } else {
          // If other engines are 0, distribute equally
          const equalWeight = Math.round(remainingWeight / otherEngines.length);
          otherEngines.forEach((key) => {
            newWeights[key] = equalWeight;
          });
        }
      }

      return newWeights;
    });
  };

  const handleSaveParameters = async () => {
    try {
      setSaving(true);

      const configData = {
        ...riskParams,
        scoringType: isModelBased ? "model_based" : "linear",
        selectedModel: isModelBased ? selectedModel : null,
        engineWeights: isModelBased ? null : engineWeights,
        thresholdType: isThresholdModelBased ? "model_based" : "manual",
        updatedAt: new Date().toISOString(),
      };

      // In a real implementation, this would save to backend
      // await riskAggregationAPI.updateParameters(configData);

      const message = isModelBased
        ? `Risk decision parameters saved successfully with ${selectedModel} model`
        : "Risk decision parameters saved successfully with linear scoring";

      onShowSnackbar(message, "success");
    } catch (error) {
      onShowSnackbar("Failed to save risk parameters", "error");
    } finally {
      setSaving(false);
    }
  };

  const getDecisionForScore = (score) => {
    if (score >= riskParams.autoRejectThreshold) {
      return { type: "REJECT", color: "#d32f2f", severity: "error" };
    } else if (score <= riskParams.autoApproveThreshold) {
      return { type: "APPROVE", color: "#2e7d32", severity: "success" };
    } else {
      return { type: "HUMAN_REVIEW", color: "#ed6c02", severity: "warning" };
    }
  };

  const decision = getDecisionForScore(currentRiskScore);

  const thresholdData = [
    {
      name: "Auto Approve",
      threshold: riskParams.autoApproveThreshold,
      range: `0% - ${riskParams.autoApproveThreshold}%`,
      description: "Low risk transactions automatically approved",
      color: "#2e7d32",
    },
    {
      name: "Human Review",
      threshold: null,
      range: `${riskParams.autoApproveThreshold + 1}% - ${
        riskParams.autoRejectThreshold - 1
      }%`,
      description: "Medium risk transactions require manual review",
      color: "#ed6c02",
    },
    {
      name: "Auto Reject",
      threshold: riskParams.autoRejectThreshold,
      range: `${riskParams.autoRejectThreshold}% - 100%`,
      description: "High risk transactions automatically rejected",
      color: "#d32f2f",
    },
  ];

  const scoringConfigData = [
    {
      name: "Scoring Type",
      value: isModelBased ? "Model-based" : "Linear",
      description: isModelBased
        ? `Using ${selectedModel.replace("_", " ")} model for risk calculation`
        : "Using weighted linear factors for risk calculation",
    },
    {
      name: "Model Version",
      value: isModelBased ? selectedModel : "N/A",
      description: isModelBased
        ? "Machine learning model version"
        : "Not applicable for linear scoring",
    },
    {
      name: "Last Updated",
      value: new Date().toLocaleDateString(),
      description: "Configuration last modified",
    },
  ];

  useEffect(() => {
    loadRiskParameters();
  }, []);

  return (
    <Box sx={{ maxWidth: 1400, mx: "auto", p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant='h4'
          sx={{ fontWeight: "bold", color: "#1a1a1a", mb: 1 }}
        >
          Risk Decision Configuration
        </Typography>
        <Typography variant='body1' color='text.secondary'>
          Configure automated decision thresholds and risk scoring parameters
          for fraud detection.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Configuration Panel */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ boxShadow: 1, border: "1px solid #e0e0e0" }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
                <SettingsIcon
                  sx={{ mr: 1.5, color: "#1976d2", fontSize: "1.5rem" }}
                />
                <Typography
                  variant='h6'
                  sx={{ fontWeight: "600", color: "#1a1a1a" }}
                >
                  Decision Thresholds
                </Typography>
              </Box>

              {/* Decision Threshold Type Toggle */}
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={isThresholdModelBased}
                        onChange={(e) =>
                          setIsThresholdModelBased(e.target.checked)
                        }
                        sx={{
                          "& .MuiSwitch-switchBase.Mui-checked": {
                            color: "#1976d2",
                          },
                          "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track":
                            {
                              backgroundColor: "#1976d2",
                            },
                        }}
                      />
                    }
                    label={
                      <Typography variant='body2' sx={{ fontWeight: "500" }}>
                        Model-based Decision Thresholds
                      </Typography>
                    }
                  />
                </Box>
                <Typography
                  variant='body2'
                  color='text.secondary'
                  sx={{ mb: 2 }}
                >
                  {isThresholdModelBased
                    ? "The model will automatically determine optimal decision thresholds based on historical data and performance metrics."
                    : "Manually configure decision thresholds for automatic approval, rejection, and human review."}
                </Typography>
              </Box>

              {/* Manual Threshold Configuration - Only show when model-based is disabled */}
              {!isThresholdModelBased && (
                <Grid container spacing={4}>
                  {/* Auto Approve Threshold */}
                  <Grid item xs={12} md={6}>
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant='subtitle2'
                        sx={{ fontWeight: "600", mb: 1, color: "#2e7d32" }}
                      >
                        Auto Approve Threshold
                      </Typography>
                      <Typography
                        variant='body2'
                        color='text.secondary'
                        sx={{ mb: 2 }}
                      >
                        Risk Score: {riskParams.autoApproveThreshold}%
                      </Typography>
                      <Slider
                        value={riskParams.autoApproveThreshold}
                        onChange={(e, value) =>
                          handleParameterChange("autoApproveThreshold", value)
                        }
                        min={0}
                        max={50}
                        step={1}
                        sx={{
                          color: "#2e7d32",
                          "& .MuiSlider-thumb": {
                            backgroundColor: "#2e7d32",
                          },
                          "& .MuiSlider-track": {
                            backgroundColor: "#2e7d32",
                          },
                        }}
                      />
                      <Typography variant='caption' color='text.secondary'>
                        Transactions with risk score ≤ this threshold are
                        automatically approved
                      </Typography>
                    </Box>
                  </Grid>

                  {/* Auto Reject Threshold */}
                  <Grid item xs={12} md={6}>
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant='subtitle2'
                        sx={{ fontWeight: "600", mb: 1, color: "#d32f2f" }}
                      >
                        Auto Reject Threshold
                      </Typography>
                      <Typography
                        variant='body2'
                        color='text.secondary'
                        sx={{ mb: 2 }}
                      >
                        Risk Score: {riskParams.autoRejectThreshold}%
                      </Typography>
                      <Slider
                        value={riskParams.autoRejectThreshold}
                        onChange={(e, value) =>
                          handleParameterChange("autoRejectThreshold", value)
                        }
                        min={50}
                        max={100}
                        step={1}
                        sx={{
                          color: "#d32f2f",
                          "& .MuiSlider-thumb": {
                            backgroundColor: "#d32f2f",
                          },
                          "& .MuiSlider-track": {
                            backgroundColor: "#d32f2f",
                          },
                        }}
                      />
                      <Typography variant='caption' color='text.secondary'>
                        Transactions with risk score ≥ this threshold are
                        automatically rejected
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              )}

              {/* Model-based Threshold Information - Only show when model-based is enabled */}
              {isThresholdModelBased && (
                <Box sx={{ mb: 3 }}>
                  <Box
                    sx={{
                      p: 3,
                      bgcolor: "#e3f2fd",
                      borderRadius: 2,
                      border: "1px solid #bbdefb",
                    }}
                  >
                    <Typography
                      variant='subtitle2'
                      sx={{ fontWeight: "600", mb: 1, color: "#1976d2" }}
                    >
                      🤖 Model-based Thresholds Active
                    </Typography>
                    <Typography
                      variant='body2'
                      color='text.secondary'
                      sx={{ mb: 2 }}
                    >
                      The system will automatically optimize decision thresholds
                      based on:
                    </Typography>
                    <Box component='ul' sx={{ pl: 2, m: 0 }}>
                      <li>
                        <Typography variant='caption' color='text.secondary'>
                          Historical fraud patterns and detection accuracy
                        </Typography>
                      </li>
                      <li>
                        <Typography variant='caption' color='text.secondary'>
                          Real-time performance metrics and false positive rates
                        </Typography>
                      </li>
                      <li>
                        <Typography variant='caption' color='text.secondary'>
                          Business impact analysis and cost optimization
                        </Typography>
                      </li>
                      <li>
                        <Typography variant='caption' color='text.secondary'>
                          Regulatory compliance requirements
                        </Typography>
                      </li>
                    </Box>
                    <Typography
                      variant='caption'
                      color='text.secondary'
                      sx={{ mt: 2, display: "block", fontStyle: "italic" }}
                    >
                      Thresholds will be updated automatically as the model
                      learns from new data.
                    </Typography>
                  </Box>
                </Box>
              )}

              <Divider sx={{ my: 3 }} />

              {/* Risk Scoring Configuration */}
              <Box sx={{ mb: 3 }}>
                <Typography
                  variant='subtitle2'
                  sx={{ fontWeight: "600", mb: 2 }}
                >
                  Risk Scoring Configuration
                </Typography>

                {/* Model-based Toggle */}
                <FormControlLabel
                  control={
                    <Switch
                      checked={isModelBased}
                      onChange={(e) => setIsModelBased(e.target.checked)}
                      color='primary'
                    />
                  }
                  label={
                    <Typography variant='body2' sx={{ fontWeight: "500" }}>
                      Enable Model-based Risk Scoring
                    </Typography>
                  }
                  sx={{ mb: 2 }}
                />

                {/* Model Selection - Only show when model-based is enabled */}
                {isModelBased && (
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ p: 2, bgcolor: "#f5f5f5", borderRadius: 1 }}>
                      <Typography
                        variant='body2'
                        sx={{ fontWeight: "500", mb: 1, color: "#1976d2" }}
                      >
                        🤖 Default Model Active
                      </Typography>
                      <Typography
                        variant='body2'
                        color='text.secondary'
                        sx={{ mb: 1 }}
                      >
                        The system will use the default risk scoring model to
                        automatically calculate risk scores.
                      </Typography>
                      <Typography variant='caption' color='text.secondary'>
                        The default model is optimized for general fraud
                        detection and will be applied automatically.
                      </Typography>
                    </Box>
                  </Box>
                )}

                {/* Linear Configuration - Only show when model-based is disabled */}
                {!isModelBased && (
                  <Box sx={{ mt: 2 }}>
                    <Typography
                      variant='body2'
                      sx={{ fontWeight: "500", mb: 2, color: "text.secondary" }}
                    >
                      Linear Risk Scoring Parameters
                    </Typography>

                    {/* Engine Weight Configuration */}
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant='subtitle2'
                        sx={{ fontWeight: "600", mb: 2, color: "#1976d2" }}
                      >
                        Engine Weight Distribution
                      </Typography>
                      <Typography
                        variant='body2'
                        color='text.secondary'
                        sx={{ mb: 2 }}
                      >
                        Configure the relative importance of each scoring engine
                        (weights must sum to 100%)
                      </Typography>

                      <Grid container spacing={3}>
                        {/* Rule Engine Weight */}
                        <Grid item xs={12} md={4}>
                          <Box sx={{ mb: 2 }}>
                            <Typography
                              variant='body2'
                              sx={{ fontWeight: "500", mb: 1 }}
                            >
                              Rule Engine: {engineWeights.ruleEngine}%
                            </Typography>
                            <Slider
                              value={engineWeights.ruleEngine}
                              onChange={(e, value) =>
                                handleEngineWeightChange("ruleEngine", value)
                              }
                              min={0}
                              max={100}
                              step={1}
                              sx={{
                                color: "#1976d2",
                                "& .MuiSlider-thumb": {
                                  backgroundColor: "#1976d2",
                                },
                                "& .MuiSlider-track": {
                                  backgroundColor: "#1976d2",
                                },
                              }}
                            />
                            <Typography
                              variant='caption'
                              color='text.secondary'
                            >
                              Business rules and predefined logic
                            </Typography>
                          </Box>
                        </Grid>

                        {/* Anomaly Detection Weight */}
                        <Grid item xs={12} md={4}>
                          <Box sx={{ mb: 2 }}>
                            <Typography
                              variant='body2'
                              sx={{ fontWeight: "500", mb: 1 }}
                            >
                              Anomaly Detection:{" "}
                              {engineWeights.anomalyDetection}%
                            </Typography>
                            <Slider
                              value={engineWeights.anomalyDetection}
                              onChange={(e, value) =>
                                handleEngineWeightChange(
                                  "anomalyDetection",
                                  value
                                )
                              }
                              min={0}
                              max={100}
                              step={1}
                              sx={{
                                color: "#ed6c02",
                                "& .MuiSlider-thumb": {
                                  backgroundColor: "#ed6c02",
                                },
                                "& .MuiSlider-track": {
                                  backgroundColor: "#ed6c02",
                                },
                              }}
                            />
                            <Typography
                              variant='caption'
                              color='text.secondary'
                            >
                              Statistical anomaly detection
                            </Typography>
                          </Box>
                        </Grid>

                        {/* Predictive Model Weight */}
                        <Grid item xs={12} md={4}>
                          <Box sx={{ mb: 2 }}>
                            <Typography
                              variant='body2'
                              sx={{ fontWeight: "500", mb: 1 }}
                            >
                              Predictive Model: {engineWeights.predictiveModel}%
                            </Typography>
                            <Slider
                              value={engineWeights.predictiveModel}
                              onChange={(e, value) =>
                                handleEngineWeightChange(
                                  "predictiveModel",
                                  value
                                )
                              }
                              min={0}
                              max={100}
                              step={1}
                              sx={{
                                color: "#2e7d32",
                                "& .MuiSlider-thumb": {
                                  backgroundColor: "#2e7d32",
                                },
                                "& .MuiSlider-track": {
                                  backgroundColor: "#2e7d32",
                                },
                              }}
                            />
                            <Typography
                              variant='caption'
                              color='text.secondary'
                            >
                              Machine learning predictions
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>

                      {/* Weight Summary */}
                      <Box
                        sx={{
                          mt: 2,
                          p: 2,
                          bgcolor: "#f5f5f5",
                          borderRadius: 1,
                        }}
                      >
                        <Typography
                          variant='body2'
                          color='text.secondary'
                          sx={{ mb: 1 }}
                        >
                          <strong>Total Weight:</strong>{" "}
                          {Object.values(engineWeights).reduce(
                            (sum, weight) => sum + weight,
                            0
                          )}
                          %
                        </Typography>
                        {Object.values(engineWeights).reduce(
                          (sum, weight) => sum + weight,
                          0
                        ) !== 100 && (
                          <Typography variant='caption' color='error'>
                            ⚠️ Weights must sum to exactly 100%
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </Box>
                )}
              </Box>

              <Button
                variant='contained'
                startIcon={
                  saving ? <CircularProgress size={20} /> : <SaveIcon />
                }
                onClick={handleSaveParameters}
                disabled={saving}
                sx={{
                  bgcolor: "#1976d2",
                  "&:hover": { bgcolor: "#1565c0" },
                  px: 4,
                  py: 1.5,
                  fontWeight: "600",
                }}
              >
                {saving ? "Saving Configuration..." : "Save Configuration"}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Risk Score Testing */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ boxShadow: 1, border: "1px solid #e0e0e0" }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
                <AssessmentIcon
                  sx={{ mr: 1.5, color: "#1976d2", fontSize: "1.5rem" }}
                />
                <Typography
                  variant='h6'
                  sx={{ fontWeight: "600", color: "#1a1a1a" }}
                >
                  Risk Score Testing
                </Typography>
              </Box>

              <Box sx={{ textAlign: "center", mb: 3 }}>
                <Typography
                  variant='h3'
                  sx={{ fontWeight: "bold", color: "#1a1a1a", mb: 1 }}
                >
                  {currentRiskScore}
                </Typography>
                <Typography
                  variant='body2'
                  color='text.secondary'
                  sx={{ mb: 2 }}
                >
                  Test Risk Score
                </Typography>
                <Chip
                  label={decision.type.replace("_", " ")}
                  color={decision.severity}
                  sx={{ fontWeight: "600", textTransform: "uppercase" }}
                />
              </Box>

              <Box sx={{ px: 1 }}>
                <Typography
                  variant='body2'
                  color='text.secondary'
                  sx={{ mb: 2 }}
                >
                  Adjust slider to test decision thresholds
                </Typography>
                <Slider
                  value={currentRiskScore}
                  onChange={(e, value) => setCurrentRiskScore(value)}
                  min={0}
                  max={100}
                  step={1}
                  sx={{ mb: 2 }}
                />
                <Box sx={{ display: "flex", justifyContent: "space-between" }}>
                  <Typography variant='caption' color='text.secondary'>
                    0%
                  </Typography>
                  <Typography variant='caption' color='text.secondary'>
                    100%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Configuration Overview Tables */}
      <Box sx={{ mt: 4 }}>
        <Typography
          variant='h6'
          sx={{ fontWeight: "600", color: "#1a1a1a", mb: 2 }}
        >
          Current Configuration Overview
        </Typography>

        {/* Decision Thresholds Table */}
        <TableContainer
          component={Paper}
          sx={{ boxShadow: 1, border: "1px solid #e0e0e0", mb: 3 }}
        >
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: "#f5f5f5" }}>
                <TableCell sx={{ fontWeight: "600" }}>Decision Type</TableCell>
                <TableCell sx={{ fontWeight: "600" }}>
                  Risk Score Range
                </TableCell>
                <TableCell sx={{ fontWeight: "600" }}>
                  Threshold Value
                </TableCell>
                <TableCell sx={{ fontWeight: "600" }}>Description</TableCell>
                <TableCell sx={{ fontWeight: "600" }}>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {thresholdData.map((row, index) => (
                <TableRow key={index} hover>
                  <TableCell>
                    <Typography variant='body2' sx={{ fontWeight: "500" }}>
                      {row.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant='body2'
                      sx={{ fontFamily: "monospace" }}
                    >
                      {row.range}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant='body2'
                      sx={{ fontFamily: "monospace" }}
                    >
                      {row.threshold ? `${row.threshold}%` : "N/A"}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2' color='text.secondary'>
                      {row.description}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label='Active'
                      size='small'
                      sx={{
                        bgcolor: "#e8f5e8",
                        color: "#2e7d32",
                        fontWeight: "500",
                      }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Scoring Configuration Table */}
        <TableContainer
          component={Paper}
          sx={{ boxShadow: 1, border: "1px solid #e0e0e0" }}
        >
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: "#f5f5f5" }}>
                <TableCell sx={{ fontWeight: "600" }}>Configuration</TableCell>
                <TableCell sx={{ fontWeight: "600" }}>Value</TableCell>
                <TableCell sx={{ fontWeight: "600" }}>Description</TableCell>
                <TableCell sx={{ fontWeight: "600" }}>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {scoringConfigData.map((row, index) => (
                <TableRow key={index} hover>
                  <TableCell>
                    <Typography variant='body2' sx={{ fontWeight: "500" }}>
                      {row.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant='body2'
                      sx={{ fontFamily: "monospace" }}
                    >
                      {row.value}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2' color='text.secondary'>
                      {row.description}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label='Active'
                      size='small'
                      sx={{
                        bgcolor: isModelBased ? "#e3f2fd" : "#f3e5f5",
                        color: isModelBased ? "#1976d2" : "#7b1fa2",
                        fontWeight: "500",
                      }}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Box>
  );
};

export default RiskDecisionPage;
